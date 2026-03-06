from fastapi import APIRouter, HTTPException
from sqlalchemy import text
import logging
import os
from datetime import datetime
from shared.database import get_db_session

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Health check endpoint that verifies service status and database connectivity.
    
    Returns:
        Service health information including status, version, and database connectivity
    """
    try:
        logger.info("Performing health check")
        
        # Basic service info
        health_data = {
            "status": "healthy",
            "service": "DistroViz API",
            "version": "3.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "development")
        }
        
        # Test database connectivity
        try:
            with get_db_session() as session:
                # Simple query to test connection
                result = session.execute(text("SELECT 1 as test"))
                test_result = result.fetchone()
                
                if test_result and test_result.test == 1:
                    health_data["database"] = {
                        "status": "connected",
                        "type": "sqlite"
                    }
                    
                    # Get basic database stats
                    stats_queries = {
                        "plants_count": "SELECT COUNT(*) as count FROM plants",
                        "centers_count": "SELECT COUNT(*) as count FROM distribution_centers",
                        "orders_count": "SELECT COUNT(*) as count FROM orders"
                    }
                    
                    stats = {}
                    for stat_name, query in stats_queries.items():
                        try:
                            stat_result = session.execute(text(query))
                            stats[stat_name] = stat_result.fetchone().count
                        except Exception as e:
                            logger.warning(f"Failed to get {stat_name}: {e}")
                            stats[stat_name] = "unknown"
                    
                    health_data["database"]["stats"] = stats
                else:
                    health_data["database"] = {
                        "status": "error",
                        "message": "Database test query failed"
                    }
                    health_data["status"] = "degraded"
                    
        except Exception as db_error:
            logger.error(f"Database health check failed: {db_error}")
            health_data["database"] = {
                "status": "disconnected",
                "error": str(db_error)
            }
            health_data["status"] = "unhealthy"
        
        # Add system information
        health_data["system"] = {
            "python_version": os.sys.version.split()[0],
            "platform": os.sys.platform
        }
        
        # Add API endpoints status
        health_data["endpoints"] = {
            "plants": "/api/plants",
            "centers": "/api/centers",
            "orders": "/api/orders",
            "dashboard": "/api/dashboard/summary"
        }
        
        # Determine HTTP status code based on health
        if health_data["status"] == "healthy":
            status_code = 200
        elif health_data["status"] == "degraded":
            status_code = 200  # Still operational
        else:
            status_code = 503  # Service unavailable
        
        logger.info(f"Health check completed: {health_data['status']}")
        
        # Return with appropriate status code
        if status_code != 200:
            raise HTTPException(status_code=status_code, detail=health_data)
        
        return health_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        error_response = {
            "status": "error",
            "service": "DistroViz API",
            "version": "3.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }
        raise HTTPException(status_code=500, detail=error_response)

@router.get("/health/ready")
async def readiness_check():
    """
    Readiness check endpoint for container orchestration.
    
    Returns:
        Simple ready/not ready status
    """
    try:
        # Test database connection
        with get_db_session() as session:
            result = session.execute(text("SELECT 1"))
            result.fetchone()
        
        return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={"status": "not ready", "error": str(e)}
        )

@router.get("/health/live")
async def liveness_check():
    """
    Liveness check endpoint for container orchestration.
    
    Returns:
        Simple alive status
    """
    return {
        "status": "alive",
        "service": "DistroViz API",
        "timestamp": datetime.utcnow().isoformat()
    }