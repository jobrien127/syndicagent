# Environment configs
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Agworld API Configuration
    # Get your API token from Agworld support: https://help.agworld.com/en/articles/2497766-how-to-contact-agworld-customer-success
    AGWORLD_API_KEY: str = os.getenv("AGWORLD_API_KEY", "")
    # API Base URL - defaults to US instance, other options:
    # Australia: https://my.agworld.com.au/user_api/v1
    # New Zealand: https://nz.agworld.co/user_api/v1
    AGWORLD_API_BASE_URL: str = os.getenv("AGWORLD_API_BASE_URL", "https://us.agworld.co/user_api/v1")
    
    # Email Configuration
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", 587))
    EMAIL_USER: str = os.getenv("EMAIL_USER", "")
    EMAIL_PASS: str = os.getenv("EMAIL_PASS", "")

settings = Settings()
