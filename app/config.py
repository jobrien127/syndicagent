# Environment configs
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    AGWORLD_API_KEY: str = os.getenv("AGWORLD_API_KEY", "")
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", 587))
    EMAIL_USER: str = os.getenv("EMAIL_USER", "")
    EMAIL_PASS: str = os.getenv("EMAIL_PASS", "")

settings = Settings()
