from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from typing import List, Dict, Any
from app.core.config import settings

class RAGService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY, model="text-embedding-3-small")
        self.llm = ChatOpenAI(openai_api_key=settings.OPENAI_API_KEY, model="gpt-4o", temperature=0)

    def create_vector_store(self, documents: List[Document]) -> FAISS:
        return FAISS.from_documents(documents, self.embeddings)

    async def get_answer(self, vector_store: FAISS, query: str) -> Dict[str, Any]:
        # Retrieve top-k relevant chunks
        docs = vector_store.similarity_search(query, k=5)
        
        context_parts = []
        for d in docs:
            context_parts.append(f"Source: {d.metadata['file_name']}, Page: {d.metadata['page_number']}\nContent: {d.page_content}")
        
        context = "\n\n".join(context_parts)

        prompt = ChatPromptTemplate.from_template("""
        You are a helpful assistant. Answer the question strictly using the provided context.
        If the answer is not in the context, say "The answer was not found in the uploaded documents."
        
        For every claim, cite the source file and page number in brackets like [Source: filename, Page: #].
        
        Context:
        {context}
        
        Question: {question}
        """)

        chain = prompt | self.llm
        response = await chain.ainvoke({"context": context, "question": query})
        
        sources = [{"file_name": d.metadata["file_name"], "page": d.metadata["page_number"]} for d in docs]
        # Deduplicate sources
        unique_sources = list({f"{s['file_name']}-{s['page']}": s for s in sources}.values())

        return {
            "answer": response.content,
            "sources": unique_sources
        }

rag_service = RAGService()
