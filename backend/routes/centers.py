from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import logging
from shared.models import DistributionCenterResponse
from dependencies import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/centers", response_model=List[DistributionCenterResponse])
async def get_centers(db: Session = Depends(get_db)):
    """
    Get all distribution centers with their details.
    
    Returns:
        List of distribution centers with id, name, region, storage_capacity, is_active status
    """
    try:
        logger.info("Fetching all distribution centers")
        
        # Query all distribution centers
        query = text("""
            SELECT id, name, region, storage_capacity, is_active, created_at, updated_at
            FROM distribution_centers
            ORDER BY name
        """)
        
        result = db.execute(query)
        rows = result.fetchall()
        
        centers = []
        for row in rows:
            center = DistributionCenterResponse(
                id=row.id,
                name=row.name,
                region=row.region,
                storage_capacity=row.storage_capacity,
                is_active=bool(row.is_active),
                created_at=row.created_at,
                updated_at=row.updated_at
            )
            centers.append(center)
        
        logger.info(f"Retrieved {len(centers)} distribution centers")
        return centers
        
    except Exception as e:
        logger.error(f"Error fetching distribution centers: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve distribution centers: {str(e)}"
        )

@router.get("/centers/{center_id}", response_model=DistributionCenterResponse)
async def get_center(center_id: int, db: Session = Depends(get_db)):
    """
    Get a specific distribution center by ID.
    
    Args:
        center_id: The ID of the distribution center to retrieve
        
    Returns:
        Distribution center details
    """
    try:
        logger.info(f"Fetching distribution center with ID: {center_id}")
        
        query = text("""
            SELECT id, name, region, storage_capacity, is_active, created_at, updated_at
            FROM distribution_centers
            WHERE id = :center_id
        """)
        
        result = db.execute(query, {"center_id": center_id})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"Distribution center with ID {center_id} not found"
            )
        
        center = DistributionCenterResponse(
            id=row.id,
            name=row.name,
            region=row.region,
            storage_capacity=row.storage_capacity,
            is_active=bool(row.is_active),
            created_at=row.created_at,
            updated_at=row.updated_at
        )
        
        logger.info(f"Retrieved distribution center: {center.name}")
        return center
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching distribution center {center_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve distribution center: {str(e)}"
        )