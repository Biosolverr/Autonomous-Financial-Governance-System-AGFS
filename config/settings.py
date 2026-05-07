import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    PORT: int = int(os.getenv("PORT", 8000))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

settings = Settings()
