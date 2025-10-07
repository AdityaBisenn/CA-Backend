# app/core/config.py
import os

class Settings:
    PROJECT_NAME: str = "Agentic AI Layer"
    LOG_DIR: str = os.path.join(os.getcwd(), "logs")
    os.makedirs(LOG_DIR, exist_ok=True)

settings = Settings()