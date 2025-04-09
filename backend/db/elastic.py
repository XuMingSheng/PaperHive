from elasticsearch import AsyncElasticsearch
from core.config import settings


# Elasticsearch client initialization
es: AsyncElasticsearch = None

def get_elasticsearch() -> AsyncElasticsearch:
    global es
    if not es:
        es = AsyncElasticsearch(settings.es_hosts)
    return es