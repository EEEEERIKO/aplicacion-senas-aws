from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title="Aplicación Señas API",
    description="API for sign language learning application",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/readyz")
async def readiness_check():
    """Readiness check endpoint"""
    return {"status": "ready"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Aplicación Señas API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# TODO: Import and include routers for:
# - Authentication (auth)
# - DynamoDB operations (dynamo)
# - S3 presigned URLs (storage)
# Example:
# from app.api.v1 import auth, dynamo, storage
# app.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
# app.include_router(dynamo.router, prefix="/v1/dynamo", tags=["dynamo"])
# app.include_router(storage.router, prefix="/v1/storage", tags=["storage"])
