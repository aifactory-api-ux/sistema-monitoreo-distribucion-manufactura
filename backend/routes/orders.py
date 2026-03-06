from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime, date
import logging
from shared.models import OrderResponse, OrderCreate, OrderStatus
from dependencies import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    plant_id: Optional[int] = Query(None, description="Filter by plant ID"),
    center_id: Optional[int] = Query(None, description="Filter by center ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of orders to return"),
    offset: int = Query(0, ge=0, description="Number of orders to skip"),
    db: Session = Depends(get_db)
):
    """
    Get all orders with optional filtering and pagination.
    
    Returns:
        List of orders with full details including plant and center information
    """
    try:
        logger.info(f"Fetching orders with filters: status={status}, plant_id={plant_id}, center_id={center_id}")
        
        # Build dynamic query with filters
        where_conditions = []
        params = {"limit": limit, "offset": offset}
        
        if status:
            where_conditions.append("o.status = :status")
            params["status"] = status.value
            
        if plant_id:
            where_conditions.append("o.plant_id = :plant_id")
            params["plant_id"] = plant_id
            
        if center_id:
            where_conditions.append("o.center_id = :center_id")
            params["center_id"] = center_id
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        query = text(f"""
            SELECT 
                o.id, o.plant_id, o.center_id, o.quantity, o.status,
                o.order_date, o.expected_delivery_date, o.actual_delivery_date,
                o.notes, o.created_at, o.updated_at,
                p.name as plant_name, p.location as plant_location,
                dc.name as center_name, dc.region as center_region
            FROM orders o
            JOIN plants p ON o.plant_id = p.id
            JOIN distribution_centers dc ON o.center_id = dc.id
            {where_clause}
            ORDER BY o.created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        
        result = db.execute(query, params)
        rows = result.fetchall()
        
        orders = []
        for row in rows:
            order = OrderResponse(
                id=row.id,
                plant_id=row.plant_id,
                center_id=row.center_id,
                quantity=row.quantity,
                status=OrderStatus(row.status),
                order_date=row.order_date,
                expected_delivery_date=row.expected_delivery_date,
                actual_delivery_date=row.actual_delivery_date,
                notes=row.notes,
                created_at=row.created_at,
                updated_at=row.updated_at,
                plant_name=row.plant_name,
                plant_location=row.plant_location,
                center_name=row.center_name,
                center_region=row.center_region
            )
            orders.append(order)
        
        logger.info(f"Retrieved {len(orders)} orders")
        return orders
        
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve orders: {str(e)}"
        )

@router.post("/orders", response_model=OrderResponse)
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """
    Create a new order.
    
    Args:
        order_data: Order creation data
        
    Returns:
        Created order with full details
    """
    try:
        logger.info(f"Creating new order: plant_id={order_data.plant_id}, center_id={order_data.center_id}")
        
        # Validate plant exists and is active
        plant_query = text("SELECT id, name, location, is_active FROM plants WHERE id = :plant_id")
        plant_result = db.execute(plant_query, {"plant_id": order_data.plant_id})
        plant_row = plant_result.fetchone()
        
        if not plant_row:
            raise HTTPException(
                status_code=400,
                detail=f"Plant with ID {order_data.plant_id} not found"
            )
        
        if not plant_row.is_active:
            raise HTTPException(
                status_code=400,
                detail=f"Plant {plant_row.name} is not active"
            )
        
        # Validate distribution center exists and is active
        center_query = text("SELECT id, name, region, is_active FROM distribution_centers WHERE id = :center_id")
        center_result = db.execute(center_query, {"center_id": order_data.center_id})
        center_row = center_result.fetchone()
        
        if not center_row:
            raise HTTPException(
                status_code=400,
                detail=f"Distribution center with ID {order_data.center_id} not found"
            )
        
        if not center_row.is_active:
            raise HTTPException(
                status_code=400,
                detail=f"Distribution center {center_row.name} is not active"
            )
        
        # Validate dates
        if order_data.expected_delivery_date and order_data.expected_delivery_date < order_data.order_date:
            raise HTTPException(
                status_code=400,
                detail="Expected delivery date cannot be before order date"
            )
        
        # Insert new order
        insert_query = text("""
            INSERT INTO orders (
                plant_id, center_id, quantity, status, order_date,
                expected_delivery_date, notes, created_at
            ) VALUES (
                :plant_id, :center_id, :quantity, :status, :order_date,
                :expected_delivery_date, :notes, :created_at
            )
        """)
        
        now = datetime.utcnow()
        insert_params = {
            "plant_id": order_data.plant_id,
            "center_id": order_data.center_id,
            "quantity": order_data.quantity,
            "status": order_data.status.value,
            "order_date": order_data.order_date,
            "expected_delivery_date": order_data.expected_delivery_date,
            "notes": order_data.notes,
            "created_at": now
        }
        
        insert_result = db.execute(insert_query, insert_params)
        db.commit()

        # Get the created order ID (portable: works on SQLite and PostgreSQL)
        order_id = insert_result.lastrowid
        
        # Fetch the complete created order
        fetch_query = text("""
            SELECT 
                o.id, o.plant_id, o.center_id, o.quantity, o.status,
                o.order_date, o.expected_delivery_date, o.actual_delivery_date,
                o.notes, o.created_at, o.updated_at,
                p.name as plant_name, p.location as plant_location,
                dc.name as center_name, dc.region as center_region
            FROM orders o
            JOIN plants p ON o.plant_id = p.id
            JOIN distribution_centers dc ON o.center_id = dc.id
            WHERE o.id = :order_id
        """)
        
        result = db.execute(fetch_query, {"order_id": order_id})
        row = result.fetchone()
        
        created_order = OrderResponse(
            id=row.id,
            plant_id=row.plant_id,
            center_id=row.center_id,
            quantity=row.quantity,
            status=OrderStatus(row.status),
            order_date=row.order_date,
            expected_delivery_date=row.expected_delivery_date,
            actual_delivery_date=row.actual_delivery_date,
            notes=row.notes,
            created_at=row.created_at,
            updated_at=row.updated_at,
            plant_name=row.plant_name,
            plant_location=row.plant_location,
            center_name=row.center_name,
            center_region=row.center_region
        )
        
        logger.info(f"Created order with ID: {order_id}")
        return created_order
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating order: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create order: {str(e)}"
        )

@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """
    Get a specific order by ID.
    
    Args:
        order_id: The ID of the order to retrieve
        
    Returns:
        Order details with plant and center information
    """
    try:
        logger.info(f"Fetching order with ID: {order_id}")
        
        query = text("""
            SELECT 
                o.id, o.plant_id, o.center_id, o.quantity, o.status,
                o.order_date, o.expected_delivery_date, o.actual_delivery_date,
                o.notes, o.created_at, o.updated_at,
                p.name as plant_name, p.location as plant_location,
                dc.name as center_name, dc.region as center_region
            FROM orders o
            JOIN plants p ON o.plant_id = p.id
            JOIN distribution_centers dc ON o.center_id = dc.id
            WHERE o.id = :order_id
        """)
        
        result = db.execute(query, {"order_id": order_id})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"Order with ID {order_id} not found"
            )
        
        order = OrderResponse(
            id=row.id,
            plant_id=row.plant_id,
            center_id=row.center_id,
            quantity=row.quantity,
            status=OrderStatus(row.status),
            order_date=row.order_date,
            expected_delivery_date=row.expected_delivery_date,
            actual_delivery_date=row.actual_delivery_date,
            notes=row.notes,
            created_at=row.created_at,
            updated_at=row.updated_at,
            plant_name=row.plant_name,
            plant_location=row.plant_location,
            center_name=row.center_name,
            center_region=row.center_region
        )
        
        logger.info(f"Retrieved order: {order.id}")
        return order
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve order: {str(e)}"
        )