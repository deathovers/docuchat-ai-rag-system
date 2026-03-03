import os
import fitz  # PyMuPDF
from typing import List, Dict, Any, Optional
from collections import OrderedDict
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from .prompts import SYSTEM_PROMPT
from .config import GOOGLE_API_KEY, EMBEDDING_MODEL, LLM_MODEL, MAX_SESSIONS

class RAGManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RAGManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL, 
            google_api_key=GOOGLE_API_KEY
        )
        self.llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL, 
            google_api_key=GOOGLE_API_KEY,
            temperature=0
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        # LRU Cache to prevent memory leaks
        self.session_indices: OrderedDict[str, FAISS] = OrderedDict()
        self.max_sessions = MAX_SESSIONS
        self.initialized = True

    def _manage_memory(self):
        """Evict oldest session if limit reached."""
        if len(self.session_indices) >= self.max_sessions:
            self.session_indices.popitem(last=False)

    async def process_pdf(self, file_bytes: bytes, file_name: str, session_id: str):
        """Extracts text, chunks it, and updates the session's vector store."""
        documents = []
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page_num, page in enumerate(doc):
                text = page.get_text()
                if not text.strip():
                    continue
                
                chunks = self.text_splitter.split_text(text)
                for chunk in chunks:
                    documents.append(Document(
                        page_content=chunk,
                        metadata={
                            "file_name": file_name,
                            "page_number": page_num + 1,
                            "session_id": session_id
                        }
                    ))
            doc.close()
        except Exception as e:
            print(f"Error processing PDF {file_name}: {e}")
            return False

        if not documents:
            return False

        if session_id in self.session_indices:
            self.session_indices[session_id].add_documents(documents)
            self.session_indices.move_to_end(session_id)
        else:
            self._manage_memory()
            self.session_indices[session_id] = FAISS.from_documents(documents, self.embeddings)
        
        return True

    async def chat(self, session_id: str, query: str, history: List[Dict[str, str]]):
        """Retrieves context and generates a grounded response."""
        if session_id not in self.session_indices:
            return {"answer": "No documents found for this session. Please upload PDFs first.", "sources": []}

        vectorstore = self.session_indices[session_id]
        self.session_indices.move_to_end(session_id) # Update LRU

        # Similarity Search
        docs = vectorstore.similarity_search(query, k=5)
        
        context = "\n\n".join([
            f"Source: {d.metadata['file_name']} (Page {d.metadata['page_number']})\nContent: {d.page_content}"
            for d in docs
        ])

        # Construct Prompt
        full_prompt = f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nUser Question: {query}"
        
        # Call Gemini
        response = await self.llm.ainvoke(full_prompt)
        
        # Extract unique sources
        unique_sources = []
        seen = set()
        for d in docs:
            source_key = (d.metadata["file_name"], d.metadata["page_number"])
            if source_key not in seen:
                unique_sources.append({"file_name": d.metadata["file_name"], "page": d.metadata["page_number"]})
                seen.add(source_key)
        
        return {
            "answer": response.content,
            "sources": unique_sources
        }

rag_manager = RAGManager()
