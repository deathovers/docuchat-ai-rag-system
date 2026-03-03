from pydantic import BaseModel
from typing import List, Optional

class Source(BaseModel):
    document: str
    page: int

class ChatRequest(BaseModel):
    query: str
    session_id: str
    history: List[dict] = []

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]

class UploadResponse(BaseModel):
    filenames: List[str]
    status: str
    session_id: str
