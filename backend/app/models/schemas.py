from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    query: str
    session_id: str
    history: List[dict] = []

class Source(BaseModel):
    doc_name: str
    page_number: int

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
