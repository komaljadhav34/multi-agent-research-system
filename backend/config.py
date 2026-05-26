import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

class Settings:
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    
    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./research.db")
    
    # Mock Mode determination
    @property
    def is_mock_mode(self) -> bool:
        # If API keys are missing, fall back to mock mode
        missing_groq = not self.GROQ_API_KEY
        missing_tavily = not self.TAVILY_API_KEY
        
        if missing_groq or missing_tavily:
            return True
        return False

settings = Settings()

# Debug printing config status
print("=== MULTI-AGENT RESEARCH SYSTEM CONFIGURATION ===")
print(f"Database URL: {settings.DATABASE_URL}")
print(f"Redis Target: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
if settings.is_mock_mode:
    print("[WARN] API Keys missing (GROQ_API_KEY and/or TAVILY_API_KEY).")
    print("[MOCK] RUNNING IN MOCK FALLBACK MODE (high-fidelity simulation).")
else:
    print("[LIVE] Groq & Tavily API keys detected. RUNNING IN LIVE API MODE.")
print("=================================================")
