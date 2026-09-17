from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from api.auth.routes import router as auth_router
from api.documents.routes import router as documents_router
from api.quiz.routes import router as quiz_router
from api.summary.routes import router as summary_router
from api.flashcard.routes import router as flashcard_router
from api.rag.routes import router as rag_router
from api.analytics.routes import router as analytics_router
from api.learning.routes import router as learning_router
from database.mongodb import connect_to_mongodb, close_mongodb_connection
from database.qdrant_client import init_qdrant_client, close_qdrant_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Campus Study Assistant API...")
    
    # Startup
    await connect_to_mongodb()
    await init_qdrant_client()
    logger.info("Database connections established")
    
    yield
    
    # Shutdown
    await close_mongodb_connection()
    await close_qdrant_client()
    logger.info("Database connections closed")


app = FastAPI(
    title="Campus Study Assistant API",
    description="AI-powered adaptive learning platform for college students",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://localhost:8501",
        "https://study-amp-frontend.vercel.app"  # Streamlit (legacy)
        "*"  # Allow all origins (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(documents_router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(rag_router, prefix="/api/v1/rag", tags=["RAG Q&A"])
app.include_router(summary_router, prefix="/api/v1/summary", tags=["Summary"])
app.include_router(quiz_router, prefix="/api/v1/quiz", tags=["Quiz"])
app.include_router(flashcard_router, prefix="/api/v1/flashcard", tags=["Flashcard"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(learning_router, prefix="/api/v1/learning", tags=["Adaptive Learning"])


@app.get("/")
async def root():
    return {
        "message": "Campus Study Assistant API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
