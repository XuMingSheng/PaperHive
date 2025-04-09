import pytest
from elasticsearch import AsyncElasticsearch
from core.config import settings

@pytest.fixture
async def es_client():
    es = AsyncElasticsearch(settings.es_hosts)
    all_indices = await es.indices.get(index="*")
    all_indices = list(all_indices.keys())

    # clean up test indices before yield
    for index_name in all_indices:
        if not index_name.startswith("."):
            await es.options(ignore_status=[404]).indices.delete(index=index_name)
    
    yield es

    # clean up again after test runs
    for index_name in all_indices:
        if not index_name.startswith("."):
            await es.options(ignore_status=[404]).indices.delete(index=index_name)

    await es.close()