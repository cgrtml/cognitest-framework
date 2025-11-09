"""
Order Service - Main API
Author: Çağrı Temel
Description: FastAPI application for order management
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session
from typing import Optional, List

from demo_app.order_service.database import get_db, init_db
from demo_app.order_service.models import Order, OrderStatus

app = FastAPI(
    title="Order Service",
    description="Order management and tracking",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic schemas
class OrderCreate(BaseModel):
    user_id: int
    product_name: str
    quantity: int
    unit_price: float
    shipping_address: str

    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        if v > 1000:
            raise ValueError('Quantity cannot exceed 1000')
        return v

    @validator('unit_price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return v


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    quantity: Optional[int] = None
    shipping_address: Optional[str] = None


class OrderResponse(BaseModel):
    id: int
    user_id: int
    product_name: str
    quantity: int
    unit_price: float
    total_price: float
    status: str
    shipping_address: str
    created_at: str

    class Config:
        from_attributes = True


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()


# API endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Order Service",
        "status": "running",
        "version": "1.0.0"
    }


@app.post("/api/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """
    Create a new order

    - **user_id**: ID of the user placing the order
    - **product_name**: Name of the product
    - **quantity**: Number of items (1-1000)
    - **unit_price**: Price per unit
    - **shipping_address**: Delivery address
    """
    # Calculate total price
    total_price = order_data.quantity * order_data.unit_price

    # Create new order
    new_order = Order(
        user_id=order_data.user_id,
        product_name=order_data.product_name,
        quantity=order_data.quantity,
        unit_price=order_data.unit_price,
        total_price=total_price,
        shipping_address=order_data.shipping_address,
        status=OrderStatus.PENDING
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return OrderResponse(
        id=new_order.id,
        user_id=new_order.user_id,
        product_name=new_order.product_name,
        quantity=new_order.quantity,
        unit_price=new_order.unit_price,
        total_price=new_order.total_price,
        status=new_order.status.value,
        shipping_address=new_order.shipping_address,
        created_at=new_order.created_at.isoformat()
    )


@app.get("/api/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """
    Get order by ID

    - **order_id**: Order ID
    """
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        product_name=order.product_name,
        quantity=order.quantity,
        unit_price=order.unit_price,
        total_price=order.total_price,
        status=order.status.value,
        shipping_address=order.shipping_address,
        created_at=order.created_at.isoformat()
    )


@app.get("/api/orders", response_model=List[OrderResponse])
async def list_orders(
        user_id: Optional[int] = None,
        status: Optional[OrderStatus] = None,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """
    List orders with optional filters

    - **user_id**: Filter by user ID
    - **status**: Filter by order status
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    query = db.query(Order)

    if user_id:
        query = query.filter(Order.user_id == user_id)

    if status:
        query = query.filter(Order.status == status)

    orders = query.offset(skip).limit(limit).all()

    return [
        OrderResponse(
            id=order.id,
            user_id=order.user_id,
            product_name=order.product_name,
            quantity=order.quantity,
            unit_price=order.unit_price,
            total_price=order.total_price,
            status=order.status.value,
            shipping_address=order.shipping_address,
            created_at=order.created_at.isoformat()
        )
        for order in orders
    ]


@app.put("/api/orders/{order_id}", response_model=OrderResponse)
async def update_order(
        order_id: int,
        order_update: OrderUpdate,
        db: Session = Depends(get_db)
):
    """
    Update order status or details

    - **order_id**: Order ID
    - **status**: New order status
    - **quantity**: Updated quantity
    - **shipping_address**: Updated shipping address
    """
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Update fields if provided
    if order_update.status:
        order.status = order_update.status

    if order_update.quantity:
        order.quantity = order_update.quantity
        order.total_price = order.quantity * order.unit_price

    if order_update.shipping_address:
        order.shipping_address = order_update.shipping_address

    db.commit()
    db.refresh(order)

    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        product_name=order.product_name,
        quantity=order.quantity,
        unit_price=order.unit_price,
        total_price=order.total_price,
        status=order.status.value,
        shipping_address=order.shipping_address,
        created_at=order.created_at.isoformat()
    )


@app.delete("/api/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(order_id: int, db: Session = Depends(get_db)):
    """
    Cancel an order

    - **order_id**: Order ID
    """
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    order.status = OrderStatus.CANCELLED
    db.commit()

    return None


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)