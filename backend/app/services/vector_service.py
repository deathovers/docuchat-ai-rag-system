from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from typing import List
from langchain.schema import Document
from app.core.config import settings
import os

class VectorService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        self.vector_store = Chroma(
            collection_name="docuchat_collection",
            embedding_function=self.embeddings,
            persist_directory=settings.VECTOR_DB_DIR
        )

    async def add_documents(self, documents: List[Document], session_id: str):
        for doc in documents:
            doc.metadata["session_id"] = session_id
        self.vector_store.add_documents(documents)

    async def similarity_search(self, query: str, session_id: str, k: int = 5):
        return self.vector_store.similarity_search(
            query, 
            k=k, 
            filter={"session_id": session_id}
        )

    async def delete_session_docs(self, session_id: str):
        # Chroma doesn't support direct filter delete in all versions easily, 
        # but we can get IDs and delete.
        results = self.vector_store.get(where={"session_id": session_id})
        if results["ids"]:
            self.vector_store.delete(ids=results["ids"])

    async def list_session_docs(self, session_id: str):
        results = self.vector_store.get(where={"session_id": session_id})
        # Extract unique filenames
        filenames = list(set([m["source"] for m in results["metadatas"]]))
        return filenames
