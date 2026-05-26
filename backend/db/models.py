import datetime
import uuid
from sqlalchemy import create_engine, Column, String, Text, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.config import settings

# Setup engine
# check if sqlite is being used to add special arguments (like check_same_thread)
engine_kwargs = {}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ResearchReport(Base):
    __tablename__ = "research_reports"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    query = Column(String(255), nullable=False)
    report_markdown = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True) # Contains source documents: [{title, url, snippet}]
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
