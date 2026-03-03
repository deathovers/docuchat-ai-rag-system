from pydantic import BaseModel
from typing import List

class DocumentInfo(BaseModel):
    file_id: str
    filename: str
    page_count: int

class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo]
