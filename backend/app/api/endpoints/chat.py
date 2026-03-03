from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag_service import RAGService

router = APIRouter()
rag_service = RAGService()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    response = await rag_service.generate_answer(
        query=request.query,
        session_id=request.session_id,
        history=request.history
    )
    return response
