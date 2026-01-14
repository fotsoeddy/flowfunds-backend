# FlowFunds Backend Implementation Guide

This document provides a detailed explanation of the FlowFunds frontend functionality and clear instructions for implementing the corresponding backend using Django and Django REST Framework (DRF).

## 1. Project Overview

FlowFunds is a personal finance tracking application.

- **Currency**: The system operates exclusively in **XAF**.
- **Core Philosophy**: Users register with a phone number, which becomes their first "linked account" (e.g., MoMo) with an initial balance. Users can subsequently add or remove other accounts (e.g., Orange Money, Cash) and specify their initial balances.
- **Transaction Logic**:
  - **Income**: Adds funds to a specific linked account (e.g., Receiving salary into MoMo).
  - **Expense**: Deducts funds from a specific linked account (e.g., Paying bills from Orange Money).

## 2. Core Data Models

### 2.0 Base Model

Create a shared base model using `django-extensions` to enforce consistency and use UUIDs.

- **Parent Classes**: Inherit from `TimeStampedModel` and `ActivatorModel`.
- **Purpose**: Provides `created`, `modified`, `status`, `activate_date`, and `deactivate_date` fields automatically.
- **ID**: Use `UUID` field as the primary key.

```python
# utils/models.py
import uuid
from django.db import models
from django_extensions.db.models import TimeStampedModel, ActivatorModel

class FlowFundsBaseModel(TimeStampedModel, ActivatorModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
```

### 2.1. User

Custom User model to handle authentication via phone number and profile data.

- **Inheritance**: AbstractBaseUser, PermissionsMixin, FlowFundsBaseModel.
- **Fields**:
  - `phone_number`: CharField (Unique, required). **USERNAME_FIELD**.
  - `first_name`: CharField.
  - `last_name`: CharField.
  - `profile_image`: ImageField (Upload to `profile_images/`).
  - `password`: (Standard Django field).
- **Note**: No `email` field is required for auth.

### 2.2. Account

Represents a financial source (e.g., a specific Mobile Money number).

- **Inheritance**: FlowFundsBaseModel.
- **Fields**:
  - `user`: ForeignKey to User.
  - `name`: CharField (e.g., "My MoMo", "Orange Money 2").
  - `number`: CharField (The phone number associated with this specific account, e.g., "677123456").
  - `type`: CharField/ChoiceField (Options: `cash`, `momo`, `om`, `bank`).
  - `balance`: DecimalField (Current balance).
  - `currency`: CharField (Default: "XAF", **only** XAF).

### 2.3. Transaction

Records a financial movement.

- **Inheritance**: FlowFundsBaseModel.
- **Fields**:
  - `user`: ForeignKey to User.
  - `account`: ForeignKey to Account (The account affected).
  - `type`: CharField/ChoiceField (Options: `income`, `expense`, `save`).
  - `amount`: DecimalField.
  - `category`: CharField (Optional, e.g., "Food", "Transport").
  - `reason`: CharField (Description of transaction).
  - `date`: DateTimeField (User-specified date of transaction).

## 3. API Endpoints Specification

### 3.1. Authentication & Registration

- **Auth Method**: **JWT** (JSON Web Tokens) via `djangorestframework-simplejwt`.
- **POST** `/api/auth/register/`

  - **Logic**:
    1. Create `User` with `phone_number`, `password`, `name`, `profile_image` (optional).
    2. **Automatically** create the first `Account` linked to this user.
       - `type`: (inferred or selected).
       - `number`: Same as registered `phone_number`.
       - `balance`: `initial_amount` provided in request.
  - **Input**:
    ```json
    {
      "phone_number": "677000000",
      "password": "securepassword",
      "first_name": "John",
      "initial_amount": 5000
    }
    ```
  - **Output**: User details, JWT Tokens (Access/Refresh).

- **POST** `/api/auth/login/`
  - **Input**: `phone_number`, `password`.
  - **Output**: JWT Tokens (Access/Refresh).

### 3.2. Accounts Management

- **GET** `/api/accounts/`
  - List all active accounts.
- **POST** `/api/accounts/`
  - **Purpose**: Add a new linked account (e.g., a second phone number).
  - **Input**: `name`, `type`, `number`, `initial_balance`.
  - **Logic**: Creates account with specified balance.
- **PUT/PATCH** `/api/accounts/{id}/`
  - **Purpose**: Update account details (e.g., rename label).
- **DELETE** `/api/accounts/{id}/`
  - **Purpose**: Remove a linked account.
  - **Logic**: Soft delete (set `status` to `0`).

### 3.3. Transactions

- **POST** `/api/transactions/`
  - **Logic**:
    - **Income**: Find `account` -> Increment `balance` by `amount`.
    - **Expense**: Find `account` -> Decrement `balance` by `amount`.
    - **Save**: Find `account` (source) -> Decrement `balance` by `amount`. (Optionally track in a 'Savings' virtual account).
  - **Validation**: Ensure sufficient funds for Expenses/Savings.

### 3.4. Dashboard Stats

- **GET** `/api/dashboard/summary/`
  - Returns aggregated totals.

## 4. Implementation Checklist

- [ ] Install `django-extensions` and `djangorestframework-simplejwt`.
- [ ] Create `FlowFundsBaseModel` with `UUIDField`.
- [ ] Implement Custom User Manager for phone number auth.
- [ ] Add `profile_image` to User model and configure `MEDIA_ROOT`/`MEDIA_URL` for file uploads.
- [ ] Implement `TransactionSerializer.create()` method to handle balance updates atomically (using `transaction.atomic()`).
