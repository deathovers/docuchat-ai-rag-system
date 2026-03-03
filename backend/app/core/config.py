from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    VECTOR_DB_DIR: str = "./chroma_db"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 100
    
    class Config:
        env_file = ".env"

settings = Settings()
