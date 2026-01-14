import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowfunds_back.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Account, Transaction
from rest_framework.test import APIClient

User = get_user_model()

def run_verification():
    print("Starting verification...")
    
    # Clean up
    User.objects.all().delete()
    
    client = APIClient()
    
    # 1. Register
    print("Testing Registration...")
    register_data = {
        "phone_number": "677123456",
        "password": "securepassword123",
        "first_name": "Test",
        "initial_amount": 5000
    }
    response = client.post('/api/auth/register/', register_data)
    if response.status_code == 201:
        print("Registration Successful.")
    else:
        print(f"Registration Failed: {response.data}")
        return

    user = User.objects.get(phone_number="677123456")
    account = Account.objects.get(user=user)
    print(f"User created: {user.phone_number}")
    print(f"Initial Account Balance: {account.balance}")
    assert account.balance == 5000, "Initial balance mismatch"
    assert account.number == "677123456", "Account number mismatch"

    # 2. Login
    print("Testing Login...")
    login_data = {
        "phone_number": "677123456",
        "password": "securepassword123"
    }
    response = client.post('/api/auth/login/', login_data)
    if response.status_code == 200:
        print("Login Successful.")
        access_token = response.data['access']
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    else:
        print(f"Login Failed: {response.data}")
        return

    # 3. Create Transaction (Expense)
    print("Testing Expense Transaction...")
    expense_data = {
        "type": "expense",
        "amount": 2000,
        "reason": "Test Expense",
        "account_id": str(account.id),
        "date": "2026-01-01T12:00:00Z"
    }
    response = client.post('/api/transactions/', expense_data)
    if response.status_code == 201:
        print("Expense Transaction Successful.")
    else:
        print(f"Expense Transaction Failed: {response.data}")
        return

    account.refresh_from_db()
    print(f"New Account Balance: {account.balance}")
    assert account.balance == 3000, "Balance after expense mismatch"

    # 4. Dashboard
    print("Testing Dashboard...")
    response = client.get('/api/dashboard/summary/')
    if response.status_code == 200:
        print(f"Dashboard Data: {response.data}")
        assert response.data['total_balance'] == 3000
    else:
        print(f"Dashboard Failed: {response.data}")

if __name__ == "__main__":
    run_verification()
