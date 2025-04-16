from core.config import settings
from core.logging import logger
from models import Hashtag, HashtagCreate, HashtagUpdate, HashtagListItem
from utils.hashtag_normalization import normalize_hashtag
from utils.hashatag_description import placeholder_hashtag_description
from utils.embeddings import mock_embedding, average_embeddings

from elasticsearch import AsyncElasticsearch, NotFoundError, ConflictError
from typing import List


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
            await self.es.delete(index=self.index, id=hashtag_id)
            return {"message": "deleted"}
        except NotFoundError:
            return {"error": "Hashtag not found"}, 404  
        

    async def delete_all(self):
        await self.es.delete_by_query(
            index=self.index,
            body={"query": {"match_all": {}}},
            refresh=True  # ensures deletions are visible immediately
        )
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
        

    def create_hashtag_model(self, create_data: HashtagCreate) -> Hashtag:
        name_normalized = normalize_hashtag(create_data.name)

        # Fallback to generated description if none provided
        description = create_data.description or placeholder_hashtag_description(create_data.name)

        # Fallback to generated embedding if none provided
        text_for_embedding = f"{create_data.name}: {description}"
        embedding = create_data.embedding or mock_embedding(text_for_embedding)

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


    