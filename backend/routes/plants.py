from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import logging
from shared.models import PlantResponse
from dependencies import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/plants", response_model=List[PlantResponse])
async def get_plants(db: Session = Depends(get_db)):
    """
    Get all plants with their details.
    
    Returns:
        List of plants with id, name, location, capacity, is_active status
    """
    try:
        logger.info("Fetching all plants")
        
        # Query all plants
        query = text("""
            SELECT id, name, location, capacity, is_active, created_at, updated_at
            FROM plants
            ORDER BY name
        """)
        
        result = db.execute(query)
        rows = result.fetchall()
        
        plants = []
        for row in rows:
            plant = PlantResponse(
                id=row.id,
                name=row.name,
                location=row.location,
                capacity=row.capacity,
                is_active=bool(row.is_active),
                created_at=row.created_at,
                updated_at=row.updated_at
            )
            plants.append(plant)
        
        logger.info(f"Retrieved {len(plants)} plants")
        return plants
        
    except Exception as e:
        logger.error(f"Error fetching plants: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve plants: {str(e)}"
        )

@router.get("/plants/{plant_id}", response_model=PlantResponse)
async def get_plant(plant_id: int, db: Session = Depends(get_db)):
    """
    Get a specific plant by ID.
    
    Args:
        plant_id: The ID of the plant to retrieve
        
    Returns:
        Plant details
    """
    try:
        logger.info(f"Fetching plant with ID: {plant_id}")
        
        query = text("""
            SELECT id, name, location, capacity, is_active, created_at, updated_at
            FROM plants
            WHERE id = :plant_id
        """)
        
        result = db.execute(query, {"plant_id": plant_id})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"Plant with ID {plant_id} not found"
            )
        
        plant = PlantResponse(
            id=row.id,
            name=row.name,
            location=row.location,
            capacity=row.capacity,
            is_active=bool(row.is_active),
            created_at=row.created_at,
            updated_at=row.updated_at
        )
        
        logger.info(f"Retrieved plant: {plant.name}")
        return plant
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching plant {plant_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve plant: {str(e)}"
        )