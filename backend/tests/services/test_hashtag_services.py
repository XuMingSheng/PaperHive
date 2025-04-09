import pytest
from elasticsearch import NotFoundError
from services.hashtag_service import HashtagService
from models import HashtagCreate, Hashtag, HashtagUpdate
from utils.hashtag_normalization import normalize_hashtag
from utils.embeddings import mock_embedding


@pytest.mark.asyncio
async def test_create(es_client):
    service = HashtagService(es=es_client)
    data = HashtagCreate(name="LLM")
    
    response = await service.create(data)

    expected_id = normalize_hashtag(data.name)
    es_response = await es_client.get(index=service.index, id=expected_id)
    hashtag = Hashtag(**es_response["_source"])
    
    assert hashtag.name == response.name


@pytest.mark.asyncio
async def test_get(es_client):
    service = HashtagService(es=es_client)
    data = Hashtag(name="LLM", description="LLM description", embedding=mock_embedding("LLM")) 
    await es_client.index(index=service.index, id=normalize_hashtag(data.name), document=data.model_dump())
    
    expected_id = normalize_hashtag(data.name)
    response = await service.get(expected_id)
    assert response.name == "LLM"

    response = await service.get("nonexistent-id")
    assert isinstance(response, tuple)
    assert response[1] == 404