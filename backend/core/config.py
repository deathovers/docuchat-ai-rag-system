from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GOOGLE_API_KEY: str = "YOUR_API_KEY"
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    LLM_MODEL: str = "gemini-1.5-pro"
    MAX_SESSIONS: int = 50

    class Config:
        env_file = ".env"

settings = Settings()
GOOGLE_API_KEY = settings.GOOGLE_API_KEY
EMBEDDING_MODEL = settings.EMBEDDING_MODEL
LLM_MODEL = settings.LLM_MODEL
MAX_SESSIONS = settings.MAX_SESSIONS
