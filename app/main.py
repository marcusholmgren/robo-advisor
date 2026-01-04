"""
/home/marcus/code/marcus/robo-advisor/app/main.py
Main FastAPI application.
This file initializes the FastAPI app, configures CORS, and registers the database.
RELEVANT FILES: app/database.py, app/routes.py, app/models.py
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Robo Advisor API", "version": "0.1.0", "docs": "/docs"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
