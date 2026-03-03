import chromadb
from chromadb.utils import embedding_functions
from app.core.config import settings
from typing import List, Dict, Any
import uuid

class VectorStoreService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)
        self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
            api_key=settings.OPENAI_API_KEY,
            model_name="text-embedding-3-small"
        )
        self.collection = self.client.get_or_create_collection(
            name="docuchat_collection",
            embedding_function=self.embedding_fn
        )

    def add_documents(self, chunks: List[str], metadatas: List[Dict[str, Any]], session_id: str):
        ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
        # Add session_id to every metadata entry for isolation
        for meta in metadatas:
            meta["session_id"] = session_id
            
        self.collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )

    def query(self, query_text: str, session_id: str, n_results: int = 5):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where={"session_id": session_id}
        )
        return results

    def delete_by_filename(self, filename: str, session_id: str):
        self.collection.delete(
            where={
                "$and": [
                    {"filename": filename},
                    {"session_id": session_id}
                ]
            }
        )
