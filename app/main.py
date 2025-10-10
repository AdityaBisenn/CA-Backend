# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.ingestion.routes import router as ingestion_router
from app.cdm.routes import router as cdm_router
from app.tenant.routes import firm_router, user_router
from app.auth.routes import router as auth_router
from app.api.ai_routes import router as ai_router
from app.ram.routes import router as ram_router
from app.core.database import engine, Base
from app.core.logger import log_request
import time

# Database tables are now managed by Alembic migrations
# Run: alembic upgrade head

app = FastAPI(
    title="Multi-Tenant CA Firm Management API with JWT Authentication",
    description="Secure backend for CA firms managing multiple clients with JWT authentication and data isolation",
    version="2.1.0"
)

# Add CORS middleware for frontend integration
import os
import json


# Configure CORS origins from environment variable `ALLOWED_ORIGINS`.
# Support either a JSON-style array (e.g. ["http://localhost:3000"]) or a
# comma-separated string (e.g. http://localhost:3000,http://127.0.0.1:3000).
def _parse_allowed_origins(env_val: str | None):
    if not env_val:
        return ["*"]
    env_val = env_val.strip()
    # Try JSON parse first
    try:
        parsed = json.loads(env_val)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass
    # Fallback: comma-separated
    return [o.strip() for o in env_val.split(",") if o.strip()]


allowed_origins = _parse_allowed_origins(os.getenv("ALLOWED_ORIGINS"))

# If allowed_origins is ['*'] then allow_credentials must be False to comply
# with browser CORS rules when requests include credentials.
allow_credentials = False if allowed_origins == ["*"] else True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = time.time()
    response = None
    status_code = 500  # Default for exceptions
    
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as exc:
        # Log the error but re-raise
        status_code = 500
        raise
    finally:
        duration_ms = int((time.time() - start) * 1000)
        client = None
        try:
            client = request.client.host if request.client else None
        except Exception:
            client = None

        user_agent = request.headers.get("user-agent")
        auth_present = "authorization" in request.headers
        # Avoid logging any sensitive header values; only record presence
        log_request(
            method=request.method,
            path=str(request.url.path),
            status_code=status_code,
            duration_ms=duration_ms,
            client=client,
            user_agent=user_agent,
            auth_present=auth_present,
        )
    
    return response


# Include routers
app.include_router(auth_router, prefix="/api/v1")  # Authentication routes (public)
app.include_router(firm_router, prefix="/api/v1/tenant")
app.include_router(user_router, prefix="/api/v1/tenant")
app.include_router(ingestion_router, prefix="/api/v1")
app.include_router(cdm_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")  # AI-powered features
app.include_router(ram_router, prefix="/api/v1")  # RAM Cognitive Framework

@app.get("/")
def root():
    return {
        "message": "CA Verified AI Layer Backend with RAM Cognitive Framework 🚀",
        "version": "2.1.0",
        "modules": ["ingestion", "cdm", "reconciliation", "ai-analytics", "ram-cognitive"],
        "features": ["JWT Authentication", "Multi-tenant", "AI-Powered Reconciliation", "RAM Cognitive Framework"],
        "docs": "/docs"
    }