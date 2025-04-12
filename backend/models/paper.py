from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import uuid4

class Paper(BaseModel):
    id: str
    arxiv_id: Optional[str] = None
    doi: Optional[str] = None
    title: str
    abstract: str
    year: int
    authors: list[str] = []
    hashtags: list[str] = []
    
    
class PaperCreate(BaseModel):
    arxiv_id: Optional[str] = None
    doi: Optional[str] = None
    title: str
    abstract: str
    year: int = None
    authors: List[str] = []
    hashtags: List[str] = []


class PaperUpdate(BaseModel):
    arxiv_id: Optional[str] = None
    doi: Optional[str] = None
    title: Optional[str] = None
    abstract: Optional[str] = None
    authors: Optional[List[str]] = None
    year: Optional[int] = None
    hashtags: Optional[List[str]] = None


class PaperSearchRequest(BaseModel):
    query: Optional[str] = None
    must: Optional[List[str]] = []
    should: Optional[List[str]] = []
    must_not: Optional[List[str]] = []
    size: int = 20
