"""Main FastAPI application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from tortoise.contrib.fastapi import RegisterTortoise

from app.database import get_tortoise_config
from app.routes import router


@asynccontextmanager
async def lifespan(fast_app: FastAPI):
    """Manage application lifespan events."""
    # Startup: Initialize database
    async with RegisterTortoise(
        fast_app,
        config=get_tortoise_config(),
        generate_schemas=True,
        add_exception_handlers=True,
    ):
        yield
    # Shutdown: Cleanup is handled by RegisterTortoise context manager


app = FastAPI(
    title="Robo Advisor API",
    description="A application for managing investment portfolios",
    version="0.1.0",
    lifespan=lifespan,
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["portfolios", "assets"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Robo Advisor API", "version": "0.1.0", "docs": "/docs"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
