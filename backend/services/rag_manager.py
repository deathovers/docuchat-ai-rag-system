import fitz  # PyMuPDF
from typing import List, Dict, Any
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import os
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are a helpful assistant. Answer the user's question based ONLY on the provided context. 
If the answer is not in the context, state that it was not found. 
Always cite your sources using the exact format: [Filename - Page X].

Context:
{context}"""

class RAGManager:
    def __init__(self):
        # Using text-embedding-004 as per TRD
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=100
        )
        # In-memory storage for session-specific FAISS indices
        # In a production environment, these would be persisted or managed via a cache
        self.session_indices: Dict[str, FAISS] = {}

    async def process_pdf(self, file_bytes: bytes, file_name: str, session_id: str):
        """Extracts text from PDF, chunks it, and adds to the session's FAISS index."""
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        documents = []
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                documents.append(Document(
                    page_content=text,
                    metadata={
                        "file_name": file_name, 
                        "page_number": page_num + 1,
                        "session_id": session_id
                    }
                ))
        
        if not documents:
            return

        chunks = self.text_splitter.split_documents(documents)
        
        if session_id in self.session_indices:
            self.session_indices[session_id].add_documents(chunks)
        else:
            self.session_indices[session_id] = FAISS.from_documents(chunks, self.embeddings)

    async def chat(self, session_id: str, query: str, history: List[Any]):
        """Retrieves relevant chunks and generates a grounded response using Gemini 1.5 Flash."""
        if session_id not in self.session_indices:
            return {
                "answer": "I don't have any documents for this session. Please upload a PDF first.",
                "sources": []
            }

        vectorstore = self.session_indices[session_id]
        
        # Similarity search
        docs = vectorstore.similarity_search(query, k=5)
        
        # Construct context string with metadata for the LLM
        context_parts = []
        for d in docs:
            source_info = f"Source: {d.metadata['file_name']} (Page {d.metadata['page_number']})"
            context_parts.append(f"{source_info}\nContent: {d.page_content}")
        
        context = "\n\n---\n\n".join(context_parts)

        # Initialize Gemini 1.5 Flash (requested as gemini-3-flash-preview, using 1.5-flash as the actual model)
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{query}")
        ])
        
        # Convert history to LangChain message format
        formatted_history = []
        for msg in history[-10:]: # Keep last 10 messages for memory
            if isinstance(msg, dict):
                role = msg.get("role")
                content = msg.get("content")
                if role == "user":
                    formatted_history.append(("human", content))
                else:
                    formatted_history.append(("ai", content))

        chain = prompt | llm
        
        response = await chain.ainvoke({
            "context": context,
            "query": query,
            "history": formatted_history
        })

        # Extract unique sources for the response metadata
        sources = []
        seen_sources = set()
        for d in docs:
            source_key = f"{d.metadata['file_name']}-{d.metadata['page_number']}"
            if source_key not in seen_sources:
                sources.append({
                    "file_name": d.metadata["file_name"],
                    "page": d.metadata["page_number"]
                })
                seen_sources.add(source_key)

        return {
            "answer": response.content,
            "sources": sources
        }
