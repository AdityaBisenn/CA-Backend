# app/core/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration with environment variables and connection pooling
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg2://user:password@localhost:5432/agentic_ai_db"
)

# SQLite fallback for development
if not os.getenv("DATABASE_URL"):
    SQLALCHEMY_DATABASE_URL = "sqlite:///./agentic_ai_data.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Prevents stale connections
    echo=False  # Set to True for SQL query logging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()