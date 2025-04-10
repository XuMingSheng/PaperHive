from core.config import settings
from db.elastic import get_elasticsearch
from schemas.v1 import paper_index_mapping, hashtag_index_mapping
from migrations.index_migration import is_new_mappings, init_index, migrate_index
from api.v1.routes import paper, hashtag
from utils.es_warmup import wait_for_es

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from typing import Dict

async def init_or_migrate_indices(es):
    indices = [
        {
            "alias": settings.es_paper_index,
            "schema": paper_index_mapping
        },
        {
            "alias": settings.es_hashtag_index,
            "schema": hashtag_index_mapping 
        }
    ]
    version = "1"

    for index in indices:
        alias = index["alias"]
        schema = index["schema"]
        await init_index(es=es, version=version, alias=alias, schema=schema)
        await migrate_index(es=es, version=version, alias=alias, schema=schema, delete_old=True)
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    if settings.environment == "development":
        es = get_elasticsearch()
        await wait_for_es(es)
        await init_or_migrate_indices(es)

    yield  # Yield control to the app

    # --- Shutdown ---
    if settings.environment == "development":
        es = get_elasticsearch()
        if es:
            await es.close()

app = FastAPI(title=settings.app_name, lifespan=lifespan)

@app.get("/")
def root():
    return {"message": "Hello from FastAPI + Elasticsearch"}

app.include_router(paper.router, prefix="/api/v1/papers", tags=["papers"])
app.include_router(hashtag.router, prefix="/api/v1/hashtags", tags=["hashtags"])


# @app.post("/index-paper/")
# def index_paper(paper: Paper):
#     """Index a new paper in Elasticsearch."""
#     response = 
#     return {"result": response["result"]}

# @app.get("/search/")
# def search_papers(query: str, hashtag: str = None):
#     """
#     Search for papers by query (title/abstract).
#     Optionally filter by hashtag.
#     """
#     # Build a simple match query
#     es_query = {
#         "bool": {
#             "must": [
#                 {
#                     "multi_match": {
#                         "query": query,
#                         "fields": ["title", "abstract"]
#                     }
#                 }
#             ]
#         }
#     }

#     # If hashtag filter is provided, add a term filter
#     if hashtag:
#         es_query["bool"]["filter"] = [
#             {"term": {"hashtags.keyword": hashtag}}
#         ]

#     # Execute search
#     response = es.search(index="papers", query=es_query)

#     # Format results
#     hits = [
#         {
#             "id": hit["_id"],
#             "title": hit["_source"]["title"],
#             "abstract": hit["_source"]["abstract"],
#             "hashtags": hit["_source"].get("hashtags", [])
#         }
#         for hit in response["hits"]["hits"]
#     ]

#     return {"results": hits}
