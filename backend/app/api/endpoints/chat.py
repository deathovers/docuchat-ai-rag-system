from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.models.chat import ChatRequest
from app.services.vector_service import VectorService
from app.services.llm_service import LLMService
import json

router = APIRouter()
vector_service = VectorService()
llm_service = LLMService()

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # 1. Retrieve relevant chunks
    docs = await vector_service.similarity_search(request.query, request.session_id)
    context = "\n\n".join([f"Source: {d.metadata['source']}, Page: {d.metadata['page']}\nContent: {d.page_content}" for d in docs])
    
    # 2. Extract sources for the final metadata
    sources = [{"document": d.metadata["source"], "page": d.metadata["page"]} for d in docs]
    unique_sources = []
    seen = set()
    for s in sources:
        if (s["document"], s["page"]) not in seen:
            unique_sources.append(s)
            seen.add((s["document"], s["page"]))

    async def event_generator():
        # Stream the content
        async for delta in llm_service.generate_response(request.query, context, [m.dict() for m in request.history]):
            yield f"data: {json.dumps({'type': 'content', 'delta': delta})}\n\n"
        
        # Stream the sources at the end
        yield f"data: {json.dumps({'type': 'sources', 'sources': unique_sources})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
