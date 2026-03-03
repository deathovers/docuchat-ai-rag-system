from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from app.services.vector_store import VectorStoreService
from app.models.schemas import ChatResponse, Source
from typing import List

class RAGService:
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    async def generate_answer(self, query: str, session_id: str, history: List[dict]) -> ChatResponse:
        # 1. Retrieve relevant context
        search_results = self.vector_store.query(query, session_id)
        
        context_parts = []
        sources = []
        
        if not search_results["documents"] or not search_results["documents"][0]:
            return ChatResponse(
                answer="The answer was not found in the uploaded documents.",
                sources=[]
            )

        for doc, meta in zip(search_results["documents"][0], search_results["metadatas"][0]):
            context_parts.append(f"Source: {meta['filename']}, Page: {meta['page']}\nContent: {doc}")
            sources.append(Source(document=meta['filename'], page=meta['page']))

        context_text = "\n\n---\n\n".join(context_parts)

        # 2. Construct Prompt
        system_prompt = (
            "You are a document assistant. Use ONLY the provided context to answer. "
            "If the answer is not in the context, say 'The answer was not found in the uploaded documents.' "
            "Do not hallucinate. Provide a concise and accurate response."
        )
        
        messages = [SystemMessage(content=system_prompt)]
        
        # Add history if needed (simplified for MVP)
        for msg in history[-5:]: # Last 5 messages
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(SystemMessage(content=msg["content"]))

        user_prompt = f"Context:\n{context_text}\n\nQuestion: {query}"
        messages.append(HumanMessage(content=user_prompt))

        # 3. Get LLM Response
        response = await self.llm.ainvoke(messages)
        
        # 4. Deduplicate sources
        unique_sources = []
        seen = set()
        for s in sources:
            if (s.document, s.page) not in seen:
                unique_sources.append(s)
                seen.add((s.document, s.page))

        return ChatResponse(answer=response.content, sources=unique_sources)
