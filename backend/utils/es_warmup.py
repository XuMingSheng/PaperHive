import asyncio
from elasticsearch import AsyncElasticsearch, ConnectionError


async def wait_for_es(es: AsyncElasticsearch, retries=10, delay=3):
    for i in range(retries):
        try:
            if await es.ping():
                print("Elasticsearch is ready!")
                return
        except ConnectionError:
            print(f"Waiting for Elasticsearch... attempt {i+1}")
        await asyncio.sleep(delay)
    
    raise TimeoutError(f"Elasticsearch failed to start after {retries} retries")