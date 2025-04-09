from core.config import settings
from models import Hashtag, HashtagCreate, HashtagUpdate
from utils.hashtag_normalization import normalize_hashtag
from utils.hashatag_description import generate_hashtag_description
from utils.embeddings import mock_embedding

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
        
    
    async def find_all(self, size: int = 1000) -> List[Hashtag]:
        # size=1000 is the default max for Elasticsearch queries
        result = await self.es.search(
            index=self.index,
            query={"match_all": {}},
            size=size
        )

        return [
            Hashtag(**hit["_source"])
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
        

    def create_hashtag_model(self, create_data: HashtagCreate) -> Hashtag:
        hashtag_id = normalize_hashtag(create_data.name)

        # Fallback to generated description if none provided
        description = create_data.description or generate_hashtag_description(create_data.name)

        # Fallback to generated embedding if none provided
        text_for_embedding = f"{create_data.name}: {description}"
        embedding = create_data.embedding or mock_embedding(text_for_embedding)

        return Hashtag(
            id=hashtag_id,
            name=create_data.name,
            description=description,
            embedding=embedding
        )

    