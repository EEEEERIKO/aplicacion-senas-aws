from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, languages, topics, levels, exercises, progress, leaderboards

app = FastAPI(
    title="Aplicación Señas API",
    description="Secure gamified sign language learning API with JWT auth",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Health endpoints
@app.get("/healthz", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/readyz", tags=["health"])
async def readiness_check():
    """Readiness check"""
    return {"status": "ready"}

@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API info"""
    return {
        "message": "Aplicación Señas API - Gamified Sign Language Learning",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth": "/v1/auth (register, login, me)",
            "languages": "/v1/languages",
            "topics": "/v1/topics (CRUD - admin protected)",
            "levels": "/v1/levels (CRUD - admin protected)",
            "exercises": "/v1/exercises (CRUD - admin protected)",
            "progress": "/v1/progress (user progress tracking)",
            "leaderboards": "/v1/leaderboards (rankings - global, topic, level)"
        },
        "authentication": "JWT Bearer token required for protected endpoints"
    }

# Include routers
app.include_router(auth.router, prefix="/v1")
app.include_router(languages.router, prefix="/v1")
app.include_router(topics.router, prefix="/v1")
app.include_router(levels.router, prefix="/v1")
app.include_router(exercises.router, prefix="/v1")
app.include_router(progress.router, prefix="/v1")
app.include_router(leaderboards.router, prefix="/v1")
