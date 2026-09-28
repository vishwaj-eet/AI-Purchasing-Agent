import os
import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine, Base, SessionLocal, get_db
from app.core.seed_data import seed_database

# Import routers
from app.api.routes_inventory import router as inventory_router
from app.api.routes_suppliers import router as suppliers_router
from app.api.routes_orders import router as orders_router
from app.api.routes_emails import router as emails_router
from app.api.routes_approvals import router as approvals_router
from app.api.routes_rag import router as rag_router
from app.api.routes_workflow import router as workflow_router
from app.api.routes_audit import router as audit_router

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("procurepulse")

# Initialize database schema
Base.metadata.create_all(bind=engine)

# Seed database on startup
def init_db():
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

init_db()

app = FastAPI(
    title=settings.APP_NAME,
    description="Production-grade AI Agents and Multi-Step Workflows for Autonomous Supply Chain & Procurement Operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(inventory_router)
app.include_router(suppliers_router)
app.include_router(orders_router)
app.include_router(emails_router)
app.include_router(approvals_router)
app.include_router(rag_router)
app.include_router(workflow_router)
app.include_router(audit_router)

# Mount Static Files (Web Dashboard)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", tags=["Dashboard"])
def get_dashboard():
    """Serves the web dashboard UI."""
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": f"{settings.APP_NAME} API running. Visit /docs for OpenAPI specifications."}

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "HEALTHY",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "llm_provider": settings.LLM_PROVIDER,
        "database": "CONNECTED"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
