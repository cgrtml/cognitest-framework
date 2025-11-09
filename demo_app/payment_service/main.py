"""
Payment Service - Main API
Author: Çağrı Temel
Description: FastAPI application for payment processing
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid
import random

from demo_app.payment_service.database import get_db, init_db
from demo_app.payment_service.models import Payment, PaymentMethod, PaymentStatus

app = FastAPI(
    title="Payment Service",
    description="Payment processing and transaction management",
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
class PaymentCreate(BaseModel):
    order_id: int
    user_id: int
    amount: float
    payment_method: PaymentMethod
    card_number: Optional[str] = None

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        if v > 1000000:
            raise ValueError('Amount exceeds maximum limit')
        return v

    @validator('card_number')
    def validate_card_number(cls, v, values):
        if 'payment_method' in values:
            method = values['payment_method']
            if method in [PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD]:
                if not v:
                    raise ValueError('Card number is required for card payments')
                # Remove spaces and dashes
                v = v.replace(' ', '').replace('-', '')
                if not v.isdigit():
                    raise ValueError('Card number must contain only digits')
                if len(v) < 13 or len(v) > 19:
                    raise ValueError('Invalid card number length')
        return v


class RefundRequest(BaseModel):
    reason: Optional[str] = "Customer request"


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    user_id: int
    amount: float
    payment_method: str
    status: str
    transaction_id: str
    card_last_four: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


# Helper functions
def simulate_payment_processing(payment_method: PaymentMethod, amount: float) -> tuple[bool, str]:
    """
    Simulate payment gateway processing
    Returns: (success: bool, response_message: str)
    """
    # Simulate random failures for testing
    success_rate = 0.95  # 95% success rate

    if random.random() < success_rate:
        return True, "Payment processed successfully"
    else:
        failures = [
            "Insufficient funds",
            "Card declined",
            "Payment gateway timeout",
            "Invalid card details",
            "Daily limit exceeded"
        ]
        return False, random.choice(failures)


def get_card_last_four(card_number: Optional[str]) -> Optional[str]:
    """Extract last 4 digits of card number"""
    if card_number:
        clean_number = card_number.replace(' ', '').replace('-', '')
        return clean_number[-4:] if len(clean_number) >= 4 else None
    return None


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()


# API endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Payment Service",
        "status": "running",
        "version": "1.0.0"
    }


@app.post("/api/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def process_payment(payment_data: PaymentCreate, db: Session = Depends(get_db)):
    """
    Process a payment transaction

    - **order_id**: ID of the order being paid
    - **user_id**: ID of the user making payment
    - **amount**: Payment amount
    - **payment_method**: Method of payment (credit_card, debit_card, paypal, etc.)
    - **card_number**: Card number (required for card payments)
    """
    # Generate unique transaction ID
    transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"

    # Create payment record
    new_payment = Payment(
        order_id=payment_data.order_id,
        user_id=payment_data.user_id,
        amount=payment_data.amount,
        payment_method=payment_data.payment_method,
        transaction_id=transaction_id,
        card_last_four=get_card_last_four(payment_data.card_number),
        status=PaymentStatus.PROCESSING
    )

    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    # Simulate payment processing
    success, response_message = simulate_payment_processing(
        payment_data.payment_method,
        payment_data.amount
    )

    # Update payment status
    if success:
        new_payment.status = PaymentStatus.COMPLETED
        new_payment.payment_gateway_response = response_message
    else:
        new_payment.status = PaymentStatus.FAILED
        new_payment.payment_gateway_response = response_message

    db.commit()
    db.refresh(new_payment)

    # Return payment response
    response = PaymentResponse(
        id=new_payment.id,
        order_id=new_payment.order_id,
        user_id=new_payment.user_id,
        amount=new_payment.amount,
        payment_method=new_payment.payment_method.value,
        status=new_payment.status.value,
        transaction_id=new_payment.transaction_id,
        card_last_four=new_payment.card_last_four,
        created_at=new_payment.created_at.isoformat()
    )

    # If payment failed, raise exception
    if not success:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "message": response_message,
                "payment": response.dict()
            }
        )

    return response


@app.get("/api/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: int, db: Session = Depends(get_db)):
    """
    Get payment by ID

    - **payment_id**: Payment ID
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    return PaymentResponse(
        id=payment.id,
        order_id=payment.order_id,
        user_id=payment.user_id,
        amount=payment.amount,
        payment_method=payment.payment_method.value,
        status=payment.status.value,
        transaction_id=payment.transaction_id,
        card_last_four=payment.card_last_four,
        created_at=payment.created_at.isoformat()
    )


@app.get("/api/payments", response_model=List[PaymentResponse])
async def list_payments(
        user_id: Optional[int] = None,
        order_id: Optional[int] = None,
        status: Optional[PaymentStatus] = None,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """
    List payments with optional filters

    - **user_id**: Filter by user ID
    - **order_id**: Filter by order ID
    - **status**: Filter by payment status
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    query = db.query(Payment)

    if user_id:
        query = query.filter(Payment.user_id == user_id)

    if order_id:
        query = query.filter(Payment.order_id == order_id)

    if status:
        query = query.filter(Payment.status == status)

    payments = query.offset(skip).limit(limit).all()

    return [
        PaymentResponse(
            id=payment.id,
            order_id=payment.order_id,
            user_id=payment.user_id,
            amount=payment.amount,
            payment_method=payment.payment_method.value,
            status=payment.status.value,
            transaction_id=payment.transaction_id,
            card_last_four=payment.card_last_four,
            created_at=payment.created_at.isoformat()
        )
        for payment in payments
    ]


@app.post("/api/payments/{payment_id}/refund", response_model=PaymentResponse)
async def refund_payment(
        payment_id: int,
        refund_data: RefundRequest,
        db: Session = Depends(get_db)
):
    """
    Process a refund for a payment

    - **payment_id**: Payment ID to refund
    - **reason**: Reason for refund
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    if payment.status != PaymentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only completed payments can be refunded"
        )

    # Process refund
    payment.status = PaymentStatus.REFUNDED
    payment.payment_gateway_response = f"Refunded: {refund_data.reason}"

    db.commit()
    db.refresh(payment)

    return PaymentResponse(
        id=payment.id,
        order_id=payment.order_id,
        user_id=payment.user_id,
        amount=payment.amount,
        payment_method=payment.payment_method.value,
        status=payment.status.value,
        transaction_id=payment.transaction_id,
        card_last_four=payment.card_last_four,
        created_at=payment.created_at.isoformat()
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)