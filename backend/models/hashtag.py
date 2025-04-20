from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from uuid import uuid4


class Hashtag(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    embedding: List[float]


class HashtagCreate(BaseModel):
    name: str
    description: Optional[str] = None
    embedding: Optional[List[float]] = None


class HashtagUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    embedding: Optional[List[float]] = None


class HashtagListItem(BaseModel):
    name: str
    description: str


class HashtagEdge(BaseModel):
    src: str
    dst: str
    weight: int
    total_cnt: int
    cnt_by_year: Dict[str, int]


class HashtagGraph(BaseModel):
    nodes: List[str]
    edges: List[HashtagEdge]