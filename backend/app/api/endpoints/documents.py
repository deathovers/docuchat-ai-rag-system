from fastapi import APIRouter, HTTPException
from app.services.vector_store import VectorStoreService

router = APIRouter()
vector_store = VectorStoreService()

@router.delete("/{filename}")
async def delete_document(filename: str, session_id: str):
    try:
        vector_store.delete_by_filename(filename, session_id)
        return {"status": "success", "message": f"Document {filename} removed from session {session_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
