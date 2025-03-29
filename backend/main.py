# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from elasticsearch import Elasticsearch

# Elasticsearch client initialization
# If Elasticsearch is running locally on default port: http://localhost:9200
es = Elasticsearch("http://localhost:9200")

app = FastAPI()

# Example data model for indexing documents
class Paper(BaseModel):
    id: str
    title: str
    abstract: str
    hashtags: list[str] = []

@app.get("/")
def root():
    return {"message": "Hello from FastAPI + Elasticsearch"}

@app.post("/index-paper/")
def index_paper(paper: Paper):
    """Index a new paper in Elasticsearch."""
    response = es.index(
        index="papers",
        id=paper.id,
        document=paper.dict()
    )
    return {"result": response["result"]}

@app.get("/search/")
def search_papers(query: str, hashtag: str = None):
    """
    Search for papers by query (title/abstract).
    Optionally filter by hashtag.
    """
    # Build a simple match query
    es_query = {
        "bool": {
            "must": [
                {
                    "multi_match": {
                        "query": query,
                        "fields": ["title", "abstract"]
                    }
                }
            ]
        }
    }

    # If hashtag filter is provided, add a term filter
    if hashtag:
        es_query["bool"]["filter"] = [
            {"term": {"hashtags.keyword": hashtag}}
        ]

    # Execute search
    response = es.search(index="papers", query=es_query)

    # Format results
    hits = [
        {
            "id": hit["_id"],
            "title": hit["_source"]["title"],
            "abstract": hit["_source"]["abstract"],
            "hashtags": hit["_source"].get("hashtags", [])
        }
        for hit in response["hits"]["hits"]
    ]

    return {"results": hits}
