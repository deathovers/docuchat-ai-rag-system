import asyncio
import os
from typing import List, Dict, Any
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from backend.core.pdf_processor import PDFProcessor

class RAGEngine:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=api_key
        )
        self.llm = genai.GenerativeModel('gemini-1.5-pro')
        self.pdf_processor = PDFProcessor()
        self.vector_stores: Dict[str, FAISS] = {}

    async def process_document(self, session_id: str, file_path: str, file_name: str):
        """Processes PDF and adds to the session's vector store."""
        # Run sync PDF processing in a thread to avoid blocking event loop
        chunks = await asyncio.to_thread(
            self.pdf_processor.process_pdf, file_path, file_name, session_id
        )
        
        if session_id not in self.vector_stores:
            # Create new index
            self.vector_stores[session_id] = await asyncio.to_thread(
                FAISS.from_documents, chunks, self.embeddings
            )
        else:
            # Add to existing index
            await asyncio.to_thread(
                self.vector_stores[session_id].add_documents, chunks
            )

    async def chat(self, session_id: str, message: str, history: List[Dict[str, str]]):
        """Performs RAG query with conversation history."""
        if session_id not in self.vector_stores:
            return {"answer": "Please upload a document first.", "sources": []}

        # Manage history length (Fix: >= for off-by-one error)
        history = self._manage_memory(history)

        # Retrieval (Async wrapper for FAISS search)
        vector_store = self.vector_stores[session_id]
        docs = await asyncio.to_thread(
            vector_store.similarity_search, message, k=5
        )
        
        context = "\n\n".join([
            f"Source: {d.metadata['file_name']} (Page {d.metadata['page_number']})\nContent: {d.page_content}" 
            for d in docs
        ])

        # Construct Prompt with History
        history_context = "\n".join([f"{m['role']}: {m['content']}" for m in history])
        
        prompt = f"""
        You are a helpful assistant. Answer the user's question based ONLY on the provided context.
        If the answer is not in the context, state that it was not found. 
        Cite your sources using [Filename - Page X] format.

        Context:
        {context}

        Conversation History:
        {history_context}

        User Question: {message}
        """

        # Reasoning (Gemini Call)
        response = await asyncio.to_thread(self.llm.generate_content, prompt)
        
        # Deduplicate sources for the response
        unique_sources = []
        seen = set()
        for d in docs:
            source_key = (d.metadata["file_name"], d.metadata["page_number"])
            if source_key not in seen:
                unique_sources.append({"file_name": d.metadata["file_name"], "page": d.metadata["page_number"]})
                seen.add(source_key)

        return {
            "answer": response.text,
            "sources": unique_sources
        }

    def _manage_memory(self, history: List[Dict[str, str]], max_len: int = 10):
        """Trims history to maintain context window."""
        if len(history) >= max_len:
            return history[-max_len:]
        return history
