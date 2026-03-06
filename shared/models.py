from datetime import datetime, date
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

# SQLAlchemy Models
class PlantModel(Base):
    __tablename__ = "plants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=False)
    capacity = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    orders = relationship("OrderModel", back_populates="plant")

class DistributionCenterModel(Base):
    __tablename__ = "distribution_centers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    region = Column(String(255), nullable=False, index=True)
    storage_capacity = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    orders = relationship("OrderModel", back_populates="distribution_center")

class OrderModel(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="CASCADE"), nullable=False, index=True)
    center_id = Column(Integer, ForeignKey("distribution_centers.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, default=OrderStatus.PENDING, index=True)
    order_date = Column(Date, nullable=False, index=True)
    expected_delivery_date = Column(Date, nullable=True)
    actual_delivery_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    plant = relationship("PlantModel", back_populates="orders")
    distribution_center = relationship("DistributionCenterModel", back_populates="orders")

# Pydantic Schemas
class PlantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    location: str = Field(..., min_length=1, max_length=255)
    capacity: int = Field(..., gt=0)
    is_active: bool = True

class PlantCreate(PlantBase):
    pass

class PlantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    location: Optional[str] = Field(None, min_length=1, max_length=255)
    capacity: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None

class Plant(PlantBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class DistributionCenterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    region: str = Field(..., min_length=1, max_length=255)
    storage_capacity: int = Field(..., gt=0)
    is_active: bool = True

class DistributionCenterCreate(DistributionCenterBase):
    pass

class DistributionCenterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    region: Optional[str] = Field(None, min_length=1, max_length=255)
    storage_capacity: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None

class DistributionCenter(DistributionCenterBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    plant_id: int = Field(..., gt=0)
    center_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    status: OrderStatus = OrderStatus.PENDING
    order_date: date
    expected_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=1000)
    
    @model_validator(mode='after')
    def validate_delivery_dates(self):
        if self.expected_delivery_date and self.expected_delivery_date < self.order_date:
            raise ValueError('Expected delivery date cannot be before order date')
        if self.actual_delivery_date and self.actual_delivery_date < self.order_date:
            raise ValueError('Actual delivery date cannot be before order date')
        return self

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    plant_id: Optional[int] = Field(None, gt=0)
    center_id: Optional[int] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, gt=0)
    status: Optional[OrderStatus] = None
    order_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=1000)

class Order(OrderBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    plant: Optional[Plant] = None
    distribution_center: Optional[DistributionCenter] = None
    
    class Config:
        from_attributes = True

class DashboardSummary(BaseModel):
    total_orders: int = Field(..., ge=0)
    fulfillment_rate: float = Field(..., ge=0.0, le=100.0)
    avg_delivery_days: float = Field(..., ge=0.0)
    active_plants: int = Field(..., ge=0)
    active_centers: int = Field(default=0, ge=0)
    recent_orders: int = Field(default=0, ge=0)
    status_distribution: dict = Field(default_factory=dict)
    orders_by_status: dict = Field(default_factory=dict)
    orders_trend: List[dict] = Field(default_factory=list)
    
class OrderTrend(BaseModel):
    date: str
    orders: int = Field(..., ge=0)
    
class StatusDistribution(BaseModel):
    status: str
    count: int = Field(..., ge=0)
    percentage: float = Field(..., ge=0.0, le=100.0)

class HealthCheck(BaseModel):
    status: str = "healthy"
    version: str = "3.0.0"
    database_connected: bool = True
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Response models — incluyen campos extra de JOINs SQL
class PlantResponse(BaseModel):
    id: int
    name: str
    location: str
    capacity: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DistributionCenterResponse(BaseModel):
    id: int
    name: str
    region: str
    storage_capacity: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    plant_id: int
    center_id: int
    quantity: int
    status: OrderStatus
    order_date: date
    expected_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    plant_name: Optional[str] = None
    plant_location: Optional[str] = None
    center_name: Optional[str] = None
    center_region: Optional[str] = None

    class Config:
        from_attributes = True