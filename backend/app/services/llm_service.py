from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from typing import List, AsyncGenerator
from app.core.config import settings
import json

class LLMService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY,
            streaming=True
        )

    async def generate_response(self, query: str, context: str, history: List[dict]) -> AsyncGenerator[str, None]:
        system_prompt = (
            "You are a helpful assistant. Answer the question ONLY using the provided context. "
            "If the answer is not in the context, say 'The answer was not found in the uploaded documents.' "
            "Always include citations in the format [Filename, Page X].\n\n"
            f"Context:\n{context}"
        )
        
        messages = [SystemMessage(content=system_prompt)]
        for msg in history[-5:]: # Sliding window
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(SystemMessage(content=msg["content"]))
        
        messages.append(HumanMessage(content=query))
        
        async for chunk in self.llm.astream(messages):
            if chunk.content:
                yield chunk.content
