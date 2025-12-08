import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseModel):
    APP_NAME: str = "ENG400 Group27 Backend"
    POSTGRES_URL: str = os.getenv(
        "POSTGRES_URL",
        "postgresql://user:password@localhost:5432/PLC_db"
    )

    # Placeholder for later features
    OLLAMA_BASE_URL: str = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434"
    )
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "phi3:mini")
    FEEDBACK_LOG_PATH: str = os.getenv(
        "FEEDBACK_LOG_PATH",
        "feedback/feedback_log.jsonl"  # planned for user feedback logging in later phase
    )


settings = Settings()
