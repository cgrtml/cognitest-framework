"""
Manual Baseline Tests
Author: Çağrı Temel
Description: Hand-written tests to establish baseline for comparison
"""

import pytest
import requests

BASE_URL_USER = "http://localhost:8000"
BASE_URL_ORDER = "http://localhost:8001"
BASE_URL_PAYMENT = "http://localhost:8002"


class TestUserService:
    """Manual tests for User Service"""

    def test_user_registration_success(self):
        """Test successful user registration"""
        response = requests.post(
            f"{BASE_URL_USER}/api/users/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "Test1234",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 201
        assert "email" in response.json()

    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        # First registration
        requests.post(
            f"{BASE_URL_USER}/api/users/register",
            json={
                "email": "duplicate@example.com",
                "username": "user1",
                "password": "Test1234"
            }
        )

        # Duplicate registration
        response = requests.post(
            f"{BASE_URL_USER}/api/users/register",
            json={
                "email": "duplicate@example.com",
                "username": "user2",
                "password": "Test1234"
            }
        )
        assert response.status_code == 409

    def test_user_registration_weak_password(self):
        """Test registration with weak password"""
        response = requests.post(
            f"{BASE_URL_USER}/api/users/register",
            json={
                "email": "weak@example.com",
                "username": "weakuser",
                "password": "weak"
            }
        )
        assert response.status_code == 422

    def test_user_login_success(self):
        """Test successful login"""
        # Register user first
        requests.post(
            f"{BASE_URL_USER}/api/users/register",
            json={
                "email": "login@example.com",
                "username": "loginuser",
                "password": "Test1234"
            }
        )

        # Login
        response = requests.post(
            f"{BASE_URL_USER}/api/users/login",
            json={
                "email": "login@example.com",
                "password": "Test1234"
            }
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_user_login_wrong_password(self):
        """Test login with wrong password"""
        response = requests.post(
            f"{BASE_URL_USER}/api/users/login",
            json={
                "email": "login@example.com",
                "password": "WrongPass123"
            }
        )
        assert response.status_code == 401


class TestOrderService:
    """Manual tests for Order Service"""

    def test_create_order_success(self):
        """Test successful order creation"""
        response = requests.post(
            f"{BASE_URL_ORDER}/api/orders",
            json={
                "user_id": 1,
                "product_name": "Test Product",
                "quantity": 2,
                "unit_price": 29.99,
                "shipping_address": "123 Test St, Test City"
            }
        )
        assert response.status_code == 201
        assert response.json()["total_price"] == 59.98

    def test_create_order_invalid_quantity(self):
        """Test order creation with invalid quantity"""
        response = requests.post(
            f"{BASE_URL_ORDER}/api/orders",
            json={
                "user_id": 1,
                "product_name": "Test Product",
                "quantity": 0,
                "unit_price": 29.99,
                "shipping_address": "123 Test St"
            }
        )
        assert response.status_code == 422

    def test_create_order_excessive_quantity(self):
        """Test order creation with quantity exceeding limit"""
        response = requests.post(
            f"{BASE_URL_ORDER}/api/orders",
            json={
                "user_id": 1,
                "product_name": "Test Product",
                "quantity": 2000,
                "unit_price": 29.99,
                "shipping_address": "123 Test St"
            }
        )
        assert response.status_code == 422

    def test_get_order_success(self):
        """Test retrieving an order"""
        # Create order first
        create_response = requests.post(
            f"{BASE_URL_ORDER}/api/orders",
            json={
                "user_id": 1,
                "product_name": "Test Product",
                "quantity": 1,
                "unit_price": 19.99,
                "shipping_address": "456 Test Ave"
            }
        )
        order_id = create_response.json()["id"]

        # Get order
        response = requests.get(f"{BASE_URL_ORDER}/api/orders/{order_id}")
        assert response.status_code == 200
        assert response.json()["id"] == order_id

    def test_get_order_not_found(self):
        """Test retrieving non-existent order"""
        response = requests.get(f"{BASE_URL_ORDER}/api/orders/99999")
        assert response.status_code == 404


class TestPaymentService:
    """Manual tests for Payment Service"""

    def test_process_payment_credit_card(self):
        """Test payment processing with credit card"""
        response = requests.post(
            f"{BASE_URL_PAYMENT}/api/payments",
            json={
                "order_id": 1,
                "user_id": 1,
                "amount": 99.99,
                "payment_method": "credit_card",
                "card_number": "4111111111111111"
            }
        )
        # Note: May return 201 or 402 due to simulated failures
        assert response.status_code in [201, 402]

    def test_process_payment_invalid_amount(self):
        """Test payment with invalid amount"""
        response = requests.post(
            f"{BASE_URL_PAYMENT}/api/payments",
            json={
                "order_id": 1,
                "user_id": 1,
                "amount": -50.00,
                "payment_method": "credit_card",
                "card_number": "4111111111111111"
            }
        )
        assert response.status_code == 422

    def test_process_payment_missing_card(self):
        """Test card payment without card number"""
        response = requests.post(
            f"{BASE_URL_PAYMENT}/api/payments",
            json={
                "order_id": 1,
                "user_id": 1,
                "amount": 50.00,
                "payment_method": "credit_card"
            }
        )
        assert response.status_code == 422

    def test_get_payment_success(self):
        """Test retrieving a payment"""
        # Create payment first
        create_response = requests.post(
            f"{BASE_URL_PAYMENT}/api/payments",
            json={
                "order_id": 1,
                "user_id": 1,
                "amount": 75.50,
                "payment_method": "paypal"
            }
        )

        if create_response.status_code == 201:
            payment_id = create_response.json()["id"]

            # Get payment
            response = requests.get(f"{BASE_URL_PAYMENT}/api/payments/{payment_id}")
            assert response.status_code == 200
            assert response.json()["id"] == payment_id

    def test_list_payments(self):
        """Test listing payments"""
        response = requests.get(f"{BASE_URL_PAYMENT}/api/payments")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestIntegration:
    """Integration tests across services"""

    def test_complete_order_workflow(self):
        """Test complete workflow: register -> order -> payment"""
        # Step 1: Register user
        user_response = requests.post(
            f"{BASE_URL_USER}/api/users/register",
            json={
                "email": "workflow@example.com",
                "username": "workflowuser",
                "password": "Test1234"
            }
        )
        assert user_response.status_code == 201
        user_id = user_response.json()["id"]

        # Step 2: Create order
        order_response = requests.post(
            f"{BASE_URL_ORDER}/api/orders",
            json={
                "user_id": user_id,
                "product_name": "Integration Test Product",
                "quantity": 3,
                "unit_price": 25.00,
                "shipping_address": "789 Integration Blvd"
            }
        )
        assert order_response.status_code == 201
        order_id = order_response.json()["id"]
        total_price = order_response.json()["total_price"]

        # Step 3: Process payment
        payment_response = requests.post(
            f"{BASE_URL_PAYMENT}/api/payments",
            json={
                "order_id": order_id,
                "user_id": user_id,
                "amount": total_price,
                "payment_method": "credit_card",
                "card_number": "4111111111111111"
            }
        )
        assert payment_response.status_code in [201, 402]