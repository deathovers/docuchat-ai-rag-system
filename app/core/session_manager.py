from typing import Dict, Optional
from langchain_community.vectorstores import FAISS

class SessionManager:
    """Manages in-memory FAISS indices for user sessions."""
    def __init__(self):
        self.sessions: Dict[str, FAISS] = {}

    def get_vector_store(self, session_id: str) -> Optional[FAISS]:
        return self.sessions.get(session_id)

    def set_vector_store(self, session_id: str, vector_store: FAISS):
        self.sessions[session_id] = vector_store

    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

# Global instance
session_manager = SessionManager()
