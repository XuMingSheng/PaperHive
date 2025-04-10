from models.paper import Paper, PaperCreate, PaperUpdate, PaperSearchRequest
from services import PaperService
from api.v1.depedencies import get_paper_service

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from typing import Optional, List

router = APIRouter()


@router.post("/", response_model=Paper)
async def create_paper(
    create_data: PaperCreate, 
    service: PaperService = Depends(get_paper_service)
):
    result =  await service.create(create_data)
    
    if isinstance(result, tuple):
        return JSONResponse(content=result[0], status_code=result[1])
     
    return result



@router.get("/{paper_id}", response_model=Paper)
async def get_paper(
    paper_id: str, 
    service: PaperService = Depends(get_paper_service)
):
    result = await service.get(paper_id)

     
    if isinstance(result, tuple):
        return JSONResponse(content=result[0], status_code=result[1])
    
    return result


@router.get("/", response_model=List[Paper])
async def list_papers(
    service: PaperService = Depends(get_paper_service)
):
    return await service.find_all()


@router.patch("/{paper_id}", response_model=Paper)
async def update_paper(
    paper_id: str, 
    updates: PaperUpdate, 
    service: PaperService = Depends(get_paper_service)
):
    result = await service.update(paper_id, updates)
    
    if isinstance(result, tuple):
        return JSONResponse(content=result[0], status_code=result[1])
    
    return result


@router.delete("/{paper_id}")
async def delete_paper(
    paper_id: str, 
    service: 
    PaperService = Depends(get_paper_service)
):
    result = await service.delete(paper_id)

    if isinstance(result, tuple):
        return JSONResponse(content=result[0], status_code=result[1])
    
    return result


@router.delete("/all")
async def delete_all_papers(
    service: PaperService = Depends(get_paper_service)
):
    return await service.delete_all()


@router.post("/search", response_model=List[Paper])
async def search_papers(
    search_request: PaperSearchRequest,
    service: PaperService = Depends(get_paper_service)
):
    return await service.search(search_request)


