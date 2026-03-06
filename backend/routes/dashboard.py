from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
from shared.models import DashboardSummary
from dependencies import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/dashboard/summary", response_model=DashboardSummary)
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Get dashboard summary with key performance indicators.
    
    Returns:
        Dashboard summary with total_orders, fulfillment_rate, avg_delivery_days, active_plants
    """
    try:
        logger.info("Calculating dashboard summary")
        
        # Get total orders count
        total_orders_query = text("SELECT COUNT(*) as total FROM orders")
        total_orders_result = db.execute(total_orders_query)
        total_orders = total_orders_result.fetchone().total
        
        # Get delivered orders count for fulfillment rate
        delivered_orders_query = text("""
            SELECT COUNT(*) as delivered 
            FROM orders 
            WHERE status = 'delivered'
        """)
        delivered_orders_result = db.execute(delivered_orders_query)
        delivered_orders = delivered_orders_result.fetchone().delivered
        
        # Calculate fulfillment rate
        fulfillment_rate = (delivered_orders / total_orders * 100) if total_orders > 0 else 0.0
        
        # Calculate average delivery days for delivered orders
        avg_delivery_query = text("""
            SELECT AVG(
                CASE 
                    WHEN actual_delivery_date IS NOT NULL AND order_date IS NOT NULL
                    THEN julianday(actual_delivery_date) - julianday(order_date)
                    ELSE NULL
                END
            ) as avg_days
            FROM orders 
            WHERE status = 'delivered' 
            AND actual_delivery_date IS NOT NULL 
            AND order_date IS NOT NULL
        """)
        avg_delivery_result = db.execute(avg_delivery_query)
        avg_delivery_row = avg_delivery_result.fetchone()
        avg_delivery_days = round(avg_delivery_row.avg_days, 1) if avg_delivery_row.avg_days else 0.0
        
        # Get active plants count
        active_plants_query = text("""
            SELECT COUNT(*) as active 
            FROM plants 
            WHERE is_active = 1
        """)
        active_plants_result = db.execute(active_plants_query)
        active_plants = active_plants_result.fetchone().active
        
        # Get order status distribution for additional insights
        status_distribution_query = text("""
            SELECT 
                status,
                COUNT(*) as count
            FROM orders 
            GROUP BY status
        """)
        status_result = db.execute(status_distribution_query)
        status_rows = status_result.fetchall()
        
        status_distribution = {}
        for row in status_rows:
            status_distribution[row.status] = row.count
        
        # Get recent orders trend (last 30 days)
        recent_orders_query = text("""
            SELECT COUNT(*) as recent_orders
            FROM orders 
            WHERE order_date >= date('now', '-30 days')
        """)
        recent_orders_result = db.execute(recent_orders_query)
        recent_orders = recent_orders_result.fetchone().recent_orders
        
        # Get active distribution centers count
        active_centers_query = text("""
            SELECT COUNT(*) as active 
            FROM distribution_centers 
            WHERE is_active = 1
        """)
        active_centers_result = db.execute(active_centers_query)
        active_centers = active_centers_result.fetchone().active
        
        # Get orders trend (last 12 months)
        trend_query = text("""
            SELECT 
                strftime('%Y-%m', order_date) as month,
                COUNT(*) as order_count,
                SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as delivered_count
            FROM orders 
            WHERE order_date >= date('now', '-12 months')
            GROUP BY strftime('%Y-%m', order_date)
            ORDER BY month
        """)
        
        trend_result = db.execute(trend_query)
        trend_rows = trend_result.fetchall()
        
        orders_trend = []
        for row in trend_rows:
            orders_trend.append({
                "date": row.month,
                "orders": row.order_count,
                "delivered": row.delivered_count,
                "fulfillment_rate": round((row.delivered_count / row.order_count * 100), 1) if row.order_count > 0 else 0
            })
        
        summary = DashboardSummary(
            total_orders=total_orders,
            fulfillment_rate=round(fulfillment_rate, 1),
            avg_delivery_days=avg_delivery_days,
            active_plants=active_plants,
            active_centers=active_centers,
            recent_orders=recent_orders,
            status_distribution=status_distribution,
            orders_trend=orders_trend
        )
        
        logger.info(f"Dashboard summary calculated: {total_orders} orders, {fulfillment_rate:.1f}% fulfillment")
        return summary
        
    except Exception as e:
        logger.error(f"Error calculating dashboard summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate dashboard summary: {str(e)}"
        )

@router.get("/dashboard/orders-trend")
async def get_orders_trend(db: Session = Depends(get_db)):
    """
    Get orders trend data for charts.
    
    Returns:
        Monthly order counts for the last 12 months
    """
    try:
        logger.info("Fetching orders trend data")
        
        trend_query = text("""
            SELECT 
                strftime('%Y-%m', order_date) as month,
                COUNT(*) as order_count,
                SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as delivered_count
            FROM orders 
            WHERE order_date >= date('now', '-12 months')
            GROUP BY strftime('%Y-%m', order_date)
            ORDER BY month
        """)
        
        result = db.execute(trend_query)
        rows = result.fetchall()
        
        trend_data = []
        for row in rows:
            trend_data.append({
                "month": row.month,
                "total_orders": row.order_count,
                "delivered_orders": row.delivered_count,
                "fulfillment_rate": round((row.delivered_count / row.order_count * 100), 1) if row.order_count > 0 else 0
            })
        
        logger.info(f"Retrieved trend data for {len(trend_data)} months")
        return {"trend_data": trend_data}
        
    except Exception as e:
        logger.error(f"Error fetching orders trend: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch orders trend: {str(e)}"
        )

@router.get("/dashboard/plant-performance")
async def get_plant_performance(db: Session = Depends(get_db)):
    """
    Get plant performance metrics.
    
    Returns:
        Performance data for each plant
    """
    try:
        logger.info("Fetching plant performance data")
        
        performance_query = text("""
            SELECT 
                p.id,
                p.name,
                p.location,
                p.capacity,
                COUNT(o.id) as total_orders,
                SUM(CASE WHEN o.status = 'delivered' THEN 1 ELSE 0 END) as delivered_orders,
                SUM(o.quantity) as total_quantity,
                AVG(
                    CASE 
                        WHEN o.actual_delivery_date IS NOT NULL AND o.order_date IS NOT NULL
                        THEN julianday(o.actual_delivery_date) - julianday(o.order_date)
                        ELSE NULL
                    END
                ) as avg_delivery_days
            FROM plants p
            LEFT JOIN orders o ON p.id = o.plant_id
            WHERE p.is_active = 1
            GROUP BY p.id, p.name, p.location, p.capacity
            ORDER BY total_orders DESC
        """)
        
        result = db.execute(performance_query)
        rows = result.fetchall()
        
        performance_data = []
        for row in rows:
            fulfillment_rate = (row.delivered_orders / row.total_orders * 100) if row.total_orders > 0 else 0
            performance_data.append({
                "plant_id": row.id,
                "plant_name": row.name,
                "location": row.location,
                "capacity": row.capacity,
                "total_orders": row.total_orders,
                "delivered_orders": row.delivered_orders,
                "total_quantity": row.total_quantity or 0,
                "fulfillment_rate": round(fulfillment_rate, 1),
                "avg_delivery_days": round(row.avg_delivery_days, 1) if row.avg_delivery_days else 0
            })
        
        logger.info(f"Retrieved performance data for {len(performance_data)} plants")
        return {"plant_performance": performance_data}
        
    except Exception as e:
        logger.error(f"Error fetching plant performance: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch plant performance: {str(e)}"
        )