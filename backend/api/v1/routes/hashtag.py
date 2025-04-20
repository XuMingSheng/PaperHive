from core.config import settings
from models import Hashtag, HashtagCreate, HashtagUpdate, HashtagListItem, HashtagGraph
from services import HashtagService
from api.v1.depedencies import get_hashtag_service

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import List

router = APIRouter()

@router.get("/search_name", response_model=List[HashtagListItem])
async def search_hashtag_by_name(
    query: str,
    service: HashtagService = Depends(get_hashtag_service)
):
    return await service.fuzzy_search_by_name(query)


@router.get("/{hashtag_id}", response_model=Hashtag)
async def get_hashtag(
    hashtag_id: str, 
    service: HashtagService = Depends(get_hashtag_service)
):
    result =  await service.get(hashtag_id)
    
    if isinstance(result, tuple):
        return JSONResponse(content=result[0], status_code=result[1])
    
    return result


@router.get("/")
async def list_hashtags(
    service: HashtagService = Depends(get_hashtag_service)
):
    return await service.find_all()


@router.post("/recommend", response_model=List[HashtagListItem])
async def recommend_hashtags(
    selected_tags: List[str],
    service: HashtagService = Depends(get_hashtag_service)
):
    return await service.recommend_related_hashtags(selected_tags)


@router.post("/graph", response_model=HashtagGraph)
async def expand_hashtag_graph(
    tags: List[str],
    steps: int = settings.default_graph_steps,
    service: HashtagService = Depends(get_hashtag_service)
):
    return await service.expand_graph(start_tags=tags, steps=steps)


@router.post("/", response_model=Hashtag)
async def create_hashtag(
    create_data: HashtagCreate, 
    service: HashtagService = Depends(get_hashtag_service)
): 
    result = await service.create(create_data)
    
    if isinstance(result, tuple):
        return JSONResponse(content=result[0], status_code=result[1])
    
    return result


@router.patch("/{hastag_id}", response_model=Hashtag)
async def update_hashtag(
    hashtag_id: str,
    updates: HashtagUpdate, 
    service: HashtagService = Depends(get_hashtag_service)
):
    result = await service.update(hashtag_id, updates)
    
    if isinstance(result, tuple):
        return JSONResponse(content=result[0], status_code=result[1])
    
    return result


@router.delete("/all")
async def delete_all_hashtags(
    service: HashtagService = Depends(get_hashtag_service)
):
    return await service.delete_all()


@router.delete("/{hashtag_id}")
async def delelte_hashtag(
    hashtag_id: str, 
    service: HashtagService = Depends(get_hashtag_service)
):
    result = await service.delete(hashtag_id)
    
    if isinstance(result, tuple):
        return JSONResponse(content=result[0], status_code=result[1])
    
    return result