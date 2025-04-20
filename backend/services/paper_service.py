from core.config import settings
from core.logging import logger
from models import Paper, PaperCreate, PaperUpdate, PaperSearchRequest
from utils.paper_id import generate_paper_id
from utils.hashtag_normalization import normalize_hashtag
from utils.hashtag_relations_update import  build_tag_pairs, update_hashtag_relations

from elasticsearch import AsyncElasticsearch, NotFoundError, ConflictError
from typing import List

class PaperService:
    def __init__(self, es: AsyncElasticsearch):
        self.es = es
        self.index = settings.es_paper_index

    async def create(self, create_data: PaperCreate):
        invalid_tags = await self.get_invalid_hashtags(create_data)
        if invalid_tags:
            return {"error": f"Unrecognized hashtags: {invalid_tags}"}, 400
        
        paper = self.create_paper_model(create_data)

        try:
            await self.es.create(
                index=self.index,
                id=paper.id,
                document=paper.model_dump(exclude_unset=True)
            )

            tag_pairs = build_tag_pairs(paper.hashtags)
            await update_hashtag_relations(self.es, tag_pairs, delta=1, year=paper.year)

        except ConflictError:
            return {"error": "Paper already exists"}, 409
        
        return paper
    
    
    async def get(self, paper_id: str) -> Paper:
        try:
            result = await self.es.get(index=self.index, id=paper_id)
            return Paper(**result["_source"])
        
        except NotFoundError:
            return {"error": "Paper not found"}, 404
        
    async def find_all(self, size: int = 1000) -> List[Paper]:
        # size=1000 is the default max for Elasticsearch queries
        result = await self.es.search(
            index=self.index,
            query={"match_all": {}},
            size=size
        )

        return [
            Paper(**hit["_source"])
            for hit in result["hits"]["hits"]
        ] 
    

    async def update(self, paper_id: str, updated_data: PaperUpdate):
        try:
            old_paper = await self.get(paper_id)
            
            if updated_data.hashtags:
                updated_data.hashtags = [normalize_hashtag(tag) for tag in updated_data.hashtag]
            
            await self.es.update(
                index=self.index, 
                id=paper_id, 
                body={"doc": updated_data.model_dump(exclude_unset=True)}
            )
            
            updated_paper = await self.get(paper_id)
            
            if updated_data.hashtags:
                self.update_hashtag_relations(old_paper, updated_paper)

            return updated_paper
        
        except NotFoundError:
            return {"error": "Paper not found"}, 404
        

    async def delete(self, paper_id: str):
        try:
            paper = self.get(paper_id)
            
            await self.es.delete(index=self.index, id=paper_id)
            
            tag_pairs = build_tag_pairs(paper.hashtags)
            await update_hashtag_relations(self.es, tag_pairs, delta=-1, year=paper.year)
            
            return {"message": "deleted"}
        except NotFoundError:
            return {"error": "Paper not found"}, 404
        
    
    async def delete_all(self):
        # Delete all papers
        await self.es.delete_by_query(
            index=self.index,
            body={"query": {"match_all": {}}},
            refresh=True  # ensures deletions are visible immediately
        )

        # Delete all hashtag co-occurrence relations
        await self.es.delete_by_query(
            index=settings.es_hashtag_relations_index,
            body={"query": {"match_all": {}}},
            refresh=True
        )
        
        return {"message": "all papers deleted"}
    

    async def search(self, search_request: PaperSearchRequest):
        es_bool_query = {
            "must": [{
                # "terms": {"hashtags": search_request.must}
                "terms_set": {
                    "hashtags": {
                        "terms": search_request.must,
                        "minimum_should_match_script": {
                            "source": "params.num_terms"
                        }
                    }
                }
            }] if search_request.must else [],
            "should": [{"terms": {"hashtags": search_request.should}}] if search_request.should else [],
            "must_not": [{"terms": {"hashtags": search_request.must_not}}] if search_request.must_not else []
        }
        
        if search_request.query:
            es_bool_query["should"].append({
                "multi_match": {
                    "query": search_request.query,
                    "fields": ["title^3", "abstract"],  # Boost title higher
                    "fuzziness": "AUTO"
                }
            })

        es_query = {
            "function_score": {
                "query": {
                    "bool": es_bool_query
                },
                "boost_mode": "sum",
                "score_mode": "sum",
                "functions": [
                    {
                        "field_value_factor": {
                            "field": "year",
                            "factor": 1,
                            "missing": 2000
                        }
                    }
                ]
            }
        }

        result = await self.es.search(
            index=self.index,
            query=es_query,
            size=search_request.size
        )

        return [
            Paper(**hit["_source"])
            for hit in result["hits"]["hits"]
        ]
         
    
    def create_paper_model(self, create_data: PaperCreate) -> Paper:
        paper_id = generate_paper_id(arxiv_id=create_data.arxiv_id, doi=create_data.doi)

        hashtags = [
            normalize_hashtag(hashtag)
            for hashtag in create_data.hashtags
        ]
        
        return Paper(
            id=paper_id,
            arxiv_id=create_data.arxiv_id,
            doi=create_data.doi,
            title=create_data.title,
            abstract=create_data.abstract,
            year=create_data.year,
            authors=create_data.authors,
            hashtags=hashtags
        )
    
    
    async def get_invalid_hashtags(self, paper: PaperCreate) -> bool:
        invalid_list = []
        for hashtag in paper.hashtags:
            try:
                hashtag = normalize_hashtag(hashtag)
                await self.es.get(index=settings.es_hashtag_index, id=hashtag)
            except NotFoundError:
                invalid_list.append(hashtag)
        return invalid_list
    
    
    async def update_hashtag_relations(self, old_paper: Paper, updated_paper: Paper):
        old_tag_pairs =  old_tag_pairs = build_tag_pairs(old_paper.hashtags)
        new_tag_pairs = build_tag_pairs(updated_paper.hashtags)
        
        if old_paper.year == updated_paper.year:
            removed = set(old_tag_pairs) - set(new_tag_pairs)
            added = set(new_tag_pairs) - set(old_tag_pairs)
            
            if removed:
                await update_hashtag_relations(self.es, list(removed), delta=-1, year=updated_paper.year)
            if added:
                await update_hashtag_relations(self.es, list(added), delta=1, year=updated_paper.year)
        else:
            await update_hashtag_relations(self.es, list(old_tag_pairs), delta=-1, year=old_paper.year)
            await update_hashtag_relations(self.es, list(new_tag_pairs), delta=+1, year=new_tag_pairs)

        
        