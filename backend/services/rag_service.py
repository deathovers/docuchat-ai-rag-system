import asyncio
import logging
from typing import List, Dict, Optional
from cachetools import TTLCache
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import fitz  # PyMuPDF

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionLockManager:
    """Prevents race conditions during session-based vector store initialization."""
    def __init__(self):
        self.locks: Dict[str, asyncio.Lock] = {}

    def get_lock(self, session_id: str) -> asyncio.Lock:
        if session_id not in self.locks:
            self.locks[session_id] = asyncio.Lock()
        return self.locks[session_id]

class RagService:
    def __init__(self):
        # Note: Ensure GOOGLE_API_KEY is set in environment
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)
        
        # FIX: Memory Leak - Use TTLCache (1 hour TTL, max 100 sessions)
        # This automatically removes old FAISS instances from memory.
        self.vector_stores = TTLCache(maxsize=100, ttl=3600)
        
        self.lock_manager = SessionLockManager()
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    async def process_document(self, session_id: str, file_name: str, file_content: bytes):
        """Processes PDF and adds to session-isolated vector store."""
        # FIX: Race Condition - Use session-specific lock to prevent concurrent index creation
        async with self.lock_manager.get_lock(session_id):
            try:
                doc = fitz.open(stream=file_content, filetype="pdf")
                documents = []
                
                for page_num, page in enumerate(doc):
                    text = page.get_text()
                    chunks = self.text_splitter.split_text(text)
                    for chunk in chunks:
                        documents.append(Document(
                            page_content=chunk,
                            metadata={"file_name": file_name, "page_number": page_num + 1}
                        ))

                if session_id in self.vector_stores:
                    # Add to existing index
                    await asyncio.to_thread(
                        self.vector_stores[session_id].add_documents, documents
                    )
                else:
                    # Initialize FAISS index for the session
                    self.vector_stores[session_id] = await asyncio.to_thread(
                        FAISS.from_documents, documents, self.embeddings
                    )
                
                logger.info(f"Processed {file_name} for session {session_id}")
            except Exception as e:
                logger.error(f"Error processing document {file_name}: {str(e)}")
                raise e

    async def chat(self, session_id: str, query: str, history: List[Dict] = None):
        """Retrieves context and generates answer using Gemini."""
        if session_id not in self.vector_stores:
            return {"answer": "No documents uploaded for this session. Please upload a PDF first.", "sources": []}

        try:
            # Similarity Search (filtered by session via the dict lookup)
            docs = await asyncio.to_thread(
                self.vector_stores[session_id].similarity_search, query, k=5
            )
            
            if not docs:
                return {"answer": "I couldn't find any relevant information in the uploaded documents.", "sources": []}

            context = "\n\n".join([
                f"Source: {d.metadata['file_name']} (Page {d.metadata['page_number']})\nContent: {d.page_content}"
                for d in docs
            ])

            prompt = f"""
            You are a helpful assistant. Answer the user's question based ONLY on the provided context.
            If the answer is not in the context, state that it was not found. 
            Cite your sources using [Filename - Page X] format.

            Context:
            {context}

            Question: {query}
            """

            # FIX: Uncaught Exception - Validate Gemini response
            # LangChain's ChatGoogleGenerativeAI handles some validation, 
            # but we check content to be safe against safety filter blocks.
            response = await self.llm.ainvoke(prompt)
            
            if not response or not response.content:
                return {
                    "answer": "The AI was unable to generate a response. This may be due to safety filters or lack of context.",
                    "sources": []
                }

            sources = []
            seen_sources = set()
            for d in docs:
                src_key = f"{d.metadata['file_name']}-{d.metadata['page_number']}"
                if src_key not in seen_sources:
                    sources.append({"file_name": d.metadata["file_name"], "page": d.metadata["page_number"]})
                    seen_sources.add(src_key)

            return {"answer": response.content, "sources": sources}

        except Exception as e:
            logger.error(f"Chat Error for session {session_id}: {str(e)}")
            return {"answer": "An internal error occurred while processing your chat request.", "sources": []}
