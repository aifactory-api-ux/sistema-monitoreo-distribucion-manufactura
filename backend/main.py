from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging
from shared.database import init_database, get_database_manager
from routes import plants, centers, orders, dashboard, health

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment validation
required_env_vars = []
for var in required_env_vars:
    if not os.getenv(var):
        raise RuntimeError(f"Required environment variable {var} is not set")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting DistroViz API service...")
    try:
        # Initialize database
        init_database()
        db_url = get_database_manager().settings.database_url
        logger.info(f"Database initialized at {db_url}")

        # Verify database connection
        from sqlalchemy import text
        with get_database_manager().session_scope() as session:
            result = session.execute(text("SELECT 1"))
            result.fetchone()
        logger.info("Database connection verified")

        # Seed demo data if database is empty
        from seed import seed_database
        with get_database_manager().session_scope() as session:
            seed_database(session)

    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down DistroViz API service...")

# Create FastAPI app
app = FastAPI(
    title="DistroViz API",
    description="Distribution Visualization API for managing plants, centers, and orders",
    version="3.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(plants.router, prefix="/api", tags=["Plants"])
app.include_router(centers.router, prefix="/api", tags=["Centers"])
app.include_router(orders.router, prefix="/api", tags=["Orders"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "DistroViz API",
        "version": "3.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "plants": "/api/plants",
            "centers": "/api/centers",
            "orders": "/api/orders",
            "dashboard": "/api/dashboard/summary"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)