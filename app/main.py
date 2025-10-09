# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.ingestion.routes import router as ingestion_router
from app.cdm.routes import router as cdm_router
from app.tenant.routes import firm_router, user_router
from app.auth.routes import router as auth_router
from app.api.ai_routes import router as ai_router
from app.core.database import engine, Base

# Database tables are now managed by Alembic migrations
# Run: alembic upgrade head

app = FastAPI(
    title="Multi-Tenant CA Firm Management API with JWT Authentication",
    description="Secure backend for CA firms managing multiple clients with JWT authentication and data isolation",
    version="2.1.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")  # Authentication routes (public)
app.include_router(firm_router, prefix="/api/v1/tenant")
app.include_router(user_router, prefix="/api/v1/tenant")
app.include_router(ingestion_router, prefix="/api/v1")
app.include_router(cdm_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")  # AI-powered features

@app.get("/")
def root():
    return {
        "message": "Agentic AI Layer Backend Running 🚀",
        "version": "2.1.0",
        "modules": ["ingestion", "cdm", "reconciliation", "ai-analytics"],
        "features": ["JWT Authentication", "Multi-tenant", "AI-Powered Reconciliation"],
        "docs": "/docs"
    }