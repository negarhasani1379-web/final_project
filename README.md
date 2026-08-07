# Final Project

## Overview

This project is a Django REST Framework based educational management system.

The project is developed with a modular architecture. Each Django application is responsible for a specific part of the system such as user management, academic processes, school management and financial operations.

---

# Installation & Setup

## 1. Clone Repository

```bash
git clone <repository-url>
cd final_project
```

## 2. Create Virtual Environment

```bash
python -m venv .venv
```

Activate virtual environment:

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Environment Configuration

Create a `.env` file in the project root and add required environment variables.

Example:

```env
SECRET_KEY=
DATABASE_NAME=
DATABASE_USER=
DATABASE_PASSWORD=
DATABASE_HOST=
DATABASE_PORT=
```

## 5. Run Database Migration

```bash
python manage.py migrate
```

## 6. Create Super User

```bash
python manage.py createsuperuser
```

## 7. Run Development Server

```bash
python manage.py runserver
```

---

# Project Structure

The project is divided into multiple Django applications:

```
account/
    User management
    Authentication
    Authorization

core/
    Shared models
    Common utilities

academic/
    Academic features

school/
    School management

finance/
    Financial operations
```

---

# Phase 1 - Account & Authentication

## Goal

The goal of Phase 1 was to implement the foundation of user management and system security.

Main objectives:

- Create a scalable user system
- Support different user roles
- Implement authentication
- Control access based on user roles
- Verify functionality using automated tests

---

# User Management Flow

A custom User Model was implemented instead of Django default User.

The reason for this decision was that the system requires additional user information and different user types.

Each user contains:

- Username
- Password
- Phone number
- Role

Available roles:

- Teacher
- Education
- Finance


User creation flow:

```
User Input
    |
    ↓
Validation
    |
    ↓
Create User
    |
    ↓
Assign Role
    |
    ↓
Save to Database
```

---

# Authentication Flow

JWT authentication is used for API authentication.

Flow:

```
User
 |
 | username + password
 ↓
Login API
 |
 ↓
Validate Credentials
 |
 ↓
Generate JWT Token
 |
 ↓
Access Token + Refresh Token
```

Access Token is used for accessing protected APIs.

Refresh Token is used to obtain a new Access Token after expiration.

---

# Authorization Flow

Authentication identifies the user.

Authorization determines whether the user has permission to perform an action.

The system uses role-based permissions.

Flow:

```
Request
 |
 ↓
JWT Verification
 |
 ↓
Identify User
 |
 ↓
Check User Role
 |
 ↓
Allow / Reject Request
```

Example:

Teacher:

```
GET /api/auth/teacher-test/

Response:
200 OK
```

Finance:

```
GET /api/auth/teacher-test/

Response:
403 Forbidden
```

---

# Implemented Features

## Custom User Model

Implemented:

- Custom User Model
- User roles
- Phone number field
- User validation


## JWT Authentication

Implemented:

- Login API
- Access Token
- Refresh Token
- Adding user role into JWT payload


## Role Based Permissions

Implemented:

- Teacher permission
- Finance permission
- Education permission


## User Creation Management Command

Implemented a custom Django management command:

```bash
python manage.py create_user
```

Supported arguments:

```
--username
--password
--phone
--role
```

Validation:

- Invalid roles are rejected
- Duplicate usernames are rejected

---

# Testing

Automated tests were created to verify Phase 1 functionality.

Implemented tests:

- Successful JWT login
- Wrong password login
- Wrong username login
- JWT role validation
- Teacher permission access
- Finance permission restriction
- Anonymous user restriction
- User creation command
- Invalid role validation
- Duplicate username validation
- Duplicate phone validation


Run tests:

```bash
python manage.py test account
```

---

# Current Limitations

Phase 1 limitations:

- Only Account and Authentication modules are completed.
- Academic, School and Finance modules are under development.
- Business APIs are not implemented yet.

---

# Useful Commands

Run server:

```bash
python manage.py runserver
```

Run tests:

```bash
python manage.py test account
```

Create migrations:

```bash
python manage.py makemigrations
```

Apply migrations:

```bash
python manage.py migrate
```

Create superuser:

```bash
python manage.py createsuperuser
```

---

# Git Workflow

The project uses feature-based branches.

Examples:

```
feature/user-model
feature/authentication
feature/jwt-tests
feature/account-tests
```

Development flow:

```
feature branch
      |
      ↓
Pull Request
      |
      ↓
dev branch
      |
      ↓
main branch
```

Completed phases will be released using version tags.
