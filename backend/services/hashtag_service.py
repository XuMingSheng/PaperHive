from core.config import settings
from core.logging import logger
from models import (
    Hashtag, 
    HashtagCreate, 
    HashtagUpdate, 
    HashtagListItem,
    HashtagEdge,
    HashtagGraph
)
from utils.hashtag_normalization import normalize_hashtag
from utils.hashatag_description import generate_hashtag_description
from utils.embeddings import generate_hashtag_embeddings, average_embeddings

from elasticsearch import AsyncElasticsearch, NotFoundError, ConflictError
from typing import List, Optional


class HashtagService:
    def __init__(self, es: AsyncElasticsearch):
        self.es = es
        self.index = settings.es_hashtag_index

    async def create(self, create_data: HashtagCreate):
        hashtag = self.create_hashtag_model(create_data)

        try:
            await self.es.create(
                index=self.index,
                id=hashtag.id,
                document=hashtag.model_dump()
            )
        except ConflictError:
            return {"error": "Hashtag already exists"}, 409
        
        return hashtag
    
    
    async def get(self, hashtag_id: str):
        try:
            result = await self.es.get(index=self.index, id=hashtag_id)
            return Hashtag(**result["_source"])
        except NotFoundError:
            return {"error": "Hashtag not found"}, 404
        
    
    async def find_all(self, size: int = 1000) -> List[HashtagListItem]:
        # size=1000 is the default max for Elasticsearch queries
        result = await self.es.search(
            index=self.index,
            query={"match_all": {}},
            size=size
        )

        return [
            HashtagListItem(**hit["_source"])
            for hit in result["hits"]["hits"]
        ] 
        

    async def update(self, hashtag_id: str, updated_data: HashtagUpdate):
        try:
            await self.es.update(
                index=self.index, 
                id=hashtag_id, 
                body={"doc": updated_data.model_dump(exclude_unset=True)}
            )

            result = await self.es.get(index=self.index, id=hashtag_id)
            return result
        
        except NotFoundError:
            return {"error": "Hashtag not found"}, 404
        

    async def delete(self, hashtag_id: str):
        try:
            # Delete the hashtag itself
            await self.es.delete(index=self.index, id=hashtag_id)
            
            # Delete all edges where it's src or dst
            await self.delete_relations(hashtag_id=hashtag_id)
            
            # Remove hashtag from all papers
            await self.delete_from_papers(hashtag_id=hashtag_id)
        
            return {"message": "deleted"}
        
        except NotFoundError:
            return {"error": "Hashtag not found"}, 404  
        

    async def delete_all(self):
        # Delete all hashtags
        await self.es.delete_by_query(
            index=self.index,
            body={"query": {"match_all": {}}},
            refresh=True  # ensures deletions are visible immediately
        )

        # Delete all hashtag relations
        await self.delete_relations()
        
        # Remove all hashtags from every paper
        await self.delete_from_papers()
        
        return {"message": "all hashtags deleted"}
    
    
    async def fuzzy_search_by_name(self, query: str, size: int = 10) -> List[HashtagListItem]:
        es_query = {
            "match": {
                "name": {
                    "query": query,
                    "fuzziness": "AUTO"
                }
            }
        }
        
        result = await self.es.search(
            index=self.index,
            query=es_query,
            size=size
        )

        return [
            HashtagListItem(**hit["_source"])
            for hit in result["hits"]["hits"]
        ]
    

    async def recommend_related_hashtags(self, selected_tags: List[str], size: int = 10) -> List[Hashtag]:
        if not selected_tags:
            return []
        
        embeddings = await self.fetch_embeddings(selected_tags)
        pooled_embedding = average_embeddings(embeddings)

        es_query = {
            "script_score": {
                "query": {
                    "bool": {
                        "must_not": [
                            {"terms": {"_id": selected_tags}}
                        ]
                    }
                },
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {"query_vector": pooled_embedding}
                }
            }
        }

        result = await self.es.search(
            index=self.index,
            query=es_query,
            size=size
        )

        return [
            HashtagListItem(**hit["_source"])
            for hit in result["hits"]["hits"]
        ]
        

    async def expand_graph(self, start_tags: List[str], steps: int=settings.default_graph_steps) -> HashtagGraph:
        seen_tags = set(start_tags)
        seen_edges = set()
        queue = list(start_tags)
        edges = []

        # BFS
        for _ in range(steps):
            if not queue:
                break
            
            es_resp = await self.es.search(
                index=settings.es_hashtag_relations_index,
                size=settings.default_graph_top_n,
                query={
                    "bool": {
                        "should": [
                            {"terms": {"src": queue}},
                            {"terms": {"dst": queue}},
                        ]
                    }
                },
                sort=[
                    {"paper_cnt_total": {"order": "desc"}}
                ]
            )
      
            queue = []
            
            for hit in es_resp["hits"]["hits"]:
                relation = hit["_source"]
                src = relation["src"]
                dst = relation["dst"]
                total_cnt = relation.get("paper_cnt_total", 1)
                cnt_by_year = relation.get("paper_cnt_by_year", {})
                cnt_by_year = {year: cnt for year, cnt in cnt_by_year.items() if cnt is not None}
                weight = total_cnt
                
                if (src, dst) not in seen_edges:
                    seen_edges.add((src, dst))
                    edges.append(HashtagEdge(
                        src=src, 
                        dst=dst,
                        weight=weight,
                        total_cnt=total_cnt, 
                        cnt_by_year=cnt_by_year
                    ))

                for tag in [src, dst]:
                    if tag not in seen_tags:
                        seen_tags.add(tag)
                        queue.append(tag)
                        
        return HashtagGraph(nodes=list(seen_tags), edges=edges)
            

    def create_hashtag_model(self, create_data: HashtagCreate) -> Hashtag:
        name_normalized = normalize_hashtag(create_data.name)

        # Fallback to generated description if none provided
        description = create_data.description or generate_hashtag_description(create_data.name)

        # Fallback to generated embedding if none provided
        text_for_embedding = f"{create_data.name}: {description}"
        embedding = create_data.embedding or generate_hashtag_embeddings(text_for_embedding)

        return Hashtag(
            id=name_normalized,
            name=name_normalized,
            description=description,
            embedding=embedding
        )
    

    async def fetch_embeddings(self, tag_ids: List[str]) -> List[List[float]]:
        embeddings = []
        for tag_id in tag_ids:
            try:
                result = await self.es.get(index=self.index, id=tag_id)
                embeddings.append(result["_source"]["embedding"])
            except NotFoundError:
                continue
        return embeddings
    
    
    async def delete_relations(self, hashtag_id: Optional[str]=None):
        if hashtag_id:
            await self.es.delete_by_query(
                index=settings.es_hashtag_relations_index,
                body={
                    "query": {
                        "bool": {
                            "should": [
                                {"term": {"src": hashtag_id}},
                                {"term": {"dst": hashtag_id}}
                            ]
                        }
                    }
                },
                refresh=True
            )
        else:
            await self.es.delete_by_query(
                index=settings.es_hashtag_relations_index,
                body={"query": {"match_all": {}}},
                refresh=True
            )

    
    async def delete_from_papers(self, hashtag_id: Optional[str]=None):
        if hashtag_id: 
            await self.es.update_by_query(
                index=settings.es_paper_index,
                body={
                    "script": {
                        "source": """
                            if (ctx._source.hashtags != null) {
                                ctx._source.hashtags.removeIf(h -> h == params.tag);
                            }
                        """,
                        "lang": "painless",
                        "params": {"tag": hashtag_id}
                    },
                    "query": {
                        "term": {"hashtags": hashtag_id}
                    }
                },
                refresh=True
            )
        else:
            await self.es.update_by_query(
                index=settings.es_paper_index,
                body={
                    "script": {
                        "source": "ctx._source.hashtags = []",
                        "lang": "painless"
                    },
                    "query": {
                        "exists": {"field": "hashtags"}
                    }
                },
                refresh=True
            )