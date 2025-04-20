from models import Hashtag, HashtagCreate, HashtagUpdate, HashtagListItem
from services import HashtagService, PdfService
from api.v1.depedencies import get_hashtag_service, get_pdf_service

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List

router = APIRouter()

@router.post("/", response_model=Hashtag)
async def create_hashtag(
    create_data: HashtagCreate, 
    service: HashtagService = Depends(get_hashtag_service)
): 
    result = await service.create(create_data)
    
    if isinstance(result, tuple):
        return JSONResponse(content=result[0], status_code=result[1])
    
    return result


@router.get("/search_name", response_model=List[HashtagListItem])
async def search_hashtag_by_name(
    query: str,
    service: HashtagService = Depends(get_hashtag_service)
):
    return await service.fuzzy_search_by_name(query)


@router.post("/recommend", response_model=List[HashtagListItem])
async def recommend_hashtags(
    selected_tags: List[str],
    service: HashtagService = Depends(get_hashtag_service)
):
    return await service.recommend_related_hashtags(selected_tags)


@router.delete("/all")
async def delete_all_hashtags(
    service: HashtagService = Depends(get_hashtag_service)
):
    return await service.delete_all()



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


@router.delete("/{hashtag_id}")
async def delelte_hashtag(
    hashtag_id: str, 
    service: HashtagService = Depends(get_hashtag_service)
):
    result = await service.delete(hashtag_id)
    
    if isinstance(result, tuple):
        return JSONResponse(content=result[0], status_code=result[1])
    
    return result



@router.post("/parse_pdf")
async def parse_pdf_from_file(
    file: UploadFile = File(...),
    service: PdfService = Depends(get_pdf_service)
):
    if file.content_type != "application/pdf":
        return JSONResponse(status_code=400, content={"error": "Invalid file type"})

    contents = await file.read()
    result = await service.extract_pdf_info(contents)

    if isinstance(result, tuple):
        return JSONResponse(content=result[0], status_code=result[1])
    
    return result
