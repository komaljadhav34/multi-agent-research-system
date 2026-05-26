import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.db.models import init_db
from backend.api.routes import router

# Configure logging style
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Multi-Agent Research System API",
    description="Backend API powered by LangGraph, Groq, Tavily, ChromaDB, and Redis with SSE streaming.",
    version="1.0.0"
)

# Enable CORS for frontend local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Startup hook to initialize database schemas
@app.on_event("startup")
def on_startup():
    logger.info("Initializing relational database schema...")
    try:
        init_db()
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

# Include core API routes router
app.include_router(router)

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "service": "Multi-Agent Research System API",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    # Start web server on port 8000
    print("🛸 Starting Multi-Agent Research System Server on http://localhost:8000...")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
