from core.config import settings
from db.elastic import get_elasticsearch
from schemas.v1 import paper_index_mapping, hashtag_index_mapping
from migrations.index_migration import is_new_mappings, init_index, migrate_index
from api.v1.routes import paper, hashtag
from utils.es_warmup import wait_for_es

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello from FastAPI + Elasticsearch"}

app.include_router(paper.router, prefix="/api/v1/papers", tags=["papers"])
app.include_router(hashtag.router, prefix="/api/v1/hashtags", tags=["hashtags"])