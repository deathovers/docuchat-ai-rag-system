from fastapi import APIRouter
from app.services.vector_service import VectorService

router = APIRouter()
vector_service = VectorService()

@router.get("/documents")
async def list_documents(session_id: str):
    docs = await vector_service.list_session_docs(session_id)
    return {"documents": docs}

@router.delete("/documents")
async def clear_session(session_id: str):
    await vector_service.delete_session_docs(session_id)
    return {"status": "session cleared"}
