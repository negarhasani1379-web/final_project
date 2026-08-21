# Final Project

## Overview

This project is a Django REST Framework based educational management system.

The project is developed with a modular architecture. Each Django application is responsible for a specific part of the system such as user management, authentication, academic processes, school management and financial operations.

The project is developed in multiple phases, with each phase adding a specific part of the system.

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

```text
account/
    User management
    Authentication
    Authorization

core/
    Shared models
    Common utilities

academic/
    Academic features
    Terms
    Classes
    Sessions
    Teacher assignments

school/
    School management

finance/
    Session reports
    Financial operations
    Teacher term rates
    Salary
```

---

# Phase 1 - Account & Authentication

## Goal

The goal of Phase 1 was to implement the foundation of user management and system security.

Main objectives:

* Create a scalable user system
* Support different user roles
* Implement authentication
* Control access based on user roles
* Verify functionality using automated tests

---

# User Management Flow

A custom User Model was implemented instead of Django's default User model.

The reason for this decision was that the system requires additional user information and different user types.

Each user contains:

* Username
* Password
* Phone number
* Role

Available roles:

* Teacher
* Education
* Finance

User creation flow:

```text
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

```text
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

The Access Token is used for accessing protected APIs.

The Refresh Token is used to obtain a new Access Token after expiration.

---

# Authorization Flow

Authentication identifies the user.

Authorization determines whether the user has permission to perform an action.

The system uses role-based permissions.

Flow:

```text
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

```text
GET /api/auth/teacher-test/

Response:
200 OK
```

Finance:

```text
GET /api/auth/teacher-test/

Response:
403 Forbidden
```

---

# Implemented Features

## Custom User Model

Implemented:

* Custom User Model
* User roles
* Phone number field
* User validation

## JWT Authentication

Implemented:

* Login API
* Access Token
* Refresh Token
* Adding user role into JWT payload

## Role Based Permissions

Implemented:

* Teacher permission
* Finance permission
* Education permission

## User Creation Management Command

Implemented a custom Django management command:

```bash
python manage.py create_user
```

Supported arguments:

```text
--username
--password
--phone
--role
```

Validation:

* Invalid roles are rejected
* Duplicate usernames are rejected
* Duplicate phone numbers are rejected

---

# Phase 1 Testing

Automated tests were created to verify Phase 1 functionality.

Implemented tests include:

* Successful JWT login
* Wrong password login
* Wrong username login
* JWT role validation
* Teacher permission access
* Finance permission restriction
* Anonymous user restriction
* User creation command
* Invalid role validation
* Duplicate username validation
* Duplicate phone validation

Run Phase 1 tests:

```bash
python manage.py test account
```

---

# Phase 2 - Academic & School Management

## Goal

The goal of Phase 2 was to implement the academic structure of the system and school management functionality.

The phase focuses on managing:

* Schools
* Terms
* Classes
* Sessions
* Teacher assignments

---

# School Management

The School module is responsible for managing schools within the system.

Implemented functionality includes:

* School creation
* School listing
* School detail
* School update
* School deletion
* School-related validation

Schools are used as the top-level entity for organizing classrooms and academic activities.

---

# Academic Management

The Academic module manages the academic structure of the system.

Main entities include:

* Term
* Class
* Session
* Teacher Assignment

Main relationship:

```text
School
   |
   ↓
Class
   |
   ↓
Session
```

Teacher assignments connect teachers to specific classes:

```text
Teacher
   |
   ↓
Teacher Assignment
   |
   ↓
Class
```

---

# Term Management

Terms define academic periods.

Each term contains information such as:

* Title
* Start date
* End date
* Term type

Validation was implemented to prevent invalid term dates.

For example:

* End date cannot be before start date.
* Overlapping terms are rejected.

---

# Class Management

Classes belong to a school and are associated with an academic term.

Implemented functionality includes:

* Class creation
* Class listing
* Class detail
* Class update
* Class deletion
* Class filtering

Classes provide the connection between schools and academic sessions.

---

# Session Management

Sessions represent individual teaching sessions belonging to a class.

A session contains information such as:

* Class
* Session date
* Session-related academic information

Sessions are later connected to Session Reports in the Finance module.

---

# Teacher Assignment

Teacher Assignment connects a teacher to a classroom.

Relationship:

```text
Teacher
   |
   ↓
Teacher Assignment
   |
   ↓
Classroom
```

This relationship is used to determine which teacher is responsible for a specific class.

---

# Academic APIs

The Academic module provides APIs for managing:

* Terms
* Classes
* Sessions
* Teacher assignments

Access to these APIs is controlled using authentication and role-based permissions.

---

# Phase 2 Testing

Automated tests were added for the academic and school functionality.

Tests cover areas such as:

* School creation and retrieval
* Class creation and retrieval
* Term validation
* Term overlap validation
* Session creation
* Session validation
* Teacher assignment
* Permission restrictions
* API behavior

Run the full test suite with:

```bash
python manage.py test
```

---

# Phase 3 - Session Reports & Financial Management

## Goal

The goal of Phase 3 was to implement the session reporting workflow and financial-related functionality.

The main focus was allowing teachers to submit session reports and allowing Education users to review and manage those reports.

---

# Session Report

A Session Report represents the result of a teaching session.

Each report is connected to:

```text
Session
   |
   ↓
Session Report
   |
   ↓
Teacher Assignment
```

A report contains information such as:

* Lesson summary
* Present count
* Absent count
* Status
* Review comment
* Late submission status
* Rejected timestamp
* Resubmission timestamp

---

# Session Report Status

Reports can have three main statuses:

```text
Pending
   |
   ├── Approved
   |
   └── Rejected
```

### Pending

The report has been submitted and is waiting for Education review.

### Approved

The report has been reviewed and approved.

### Rejected

The report has been rejected and can be corrected and resubmitted by the teacher.

---

# Session Report Workflow

The complete workflow is:

```text
Teacher
   |
   ↓
Create Session Report
   |
   ↓
Pending
   |
   ↓
Education Review
   |
   ├───────────────┐
   ↓               ↓
Approved        Rejected
                   |
                   ↓
              Teacher Edit
                   |
                   ↓
                Resubmit
                   |
                   ↓
                Pending
                   |
                   ↓
             Education Review
```

---

# Late Submission

The system automatically determines whether a report was submitted late.

A report is marked as late when it is submitted more than 48 hours after the session.

The result is stored in:

```text
is_late
```

This allows the system to track delayed session reports.

---

# Rejection & Resubmission

When Education rejects a report:

* A review comment is required.
* The rejection timestamp is stored.
* The teacher can edit the rejected report.
* The teacher can correct the report information.
* The report is automatically returned to `pending`.
* The review comment is cleared for the new review cycle.
* The resubmission timestamp is stored.

The system keeps track of both:

```text
rejected_at
resubmitted_at
```

---

# Session Report APIs

Implemented endpoints include:

```text
POST  /api/session-reports/
GET   /api/session-reports/list/
GET   /api/session-reports/review/
PATCH /api/session-reports/<id>/review/
PATCH /api/session-reports/<id>/
GET   /api/session-reports/my-summary/
```

---

# Teacher Session Reports

Teachers can view their own session reports.

The API automatically filters reports based on the authenticated teacher.

A teacher cannot access another teacher's reports through the teacher report endpoint.

---

# Education Review

Education users can review session reports.

The review list supports filtering by:

* School
* Classroom
* Teacher
* Start date
* End date

Example:

```text
GET /api/session-reports/review/?school=2&teacher=7
```

Education users can approve or reject reports.

When rejecting a report, a review comment is required.

---

# Monthly Report Summary

Teachers can view a monthly summary of their own reports.

Endpoint:

```text
GET /api/session-reports/my-summary/?month=8&year=2026
```

The response contains:

* Approved report count
* Rejected report count
* Pending report count

Example:

```json
{
    "month": 8,
    "year": 2026,
    "approved": 3,
    "rejected": 1,
    "pending": 2
}
```

---

# Financial Management

The Finance module contains financial entities related to teachers and sessions, including:

* Teacher Term Rate
* Salary
* Session Report

These entities provide the foundation for salary and financial calculations.

---

# Phase 3 Testing

Automated tests were implemented for the session report workflow.

Tests cover:

* Session report creation
* Teacher ownership validation
* Classroom validation
* Session date validation
* Late report detection
* Education review
* Report approval
* Report rejection
* Required rejection comment
* Teacher editing rejected reports
* Teacher resubmitting rejected reports
* Rejection timestamp
* Resubmission timestamp
* Teacher monthly report summary
* Role-based access restrictions

Run the Finance tests:

```bash
python manage.py test finance
```

Run the complete project test suite:

```bash
python manage.py test
```

---

# Current Project Status

The project currently contains the following completed phases:

```text
Phase 1
Account & Authentication
        |
        ↓
Phase 2
Academic & School Management
        |
        ↓
Phase 3
Session Reports & Financial Management
```

Current implemented functionality includes:

* Custom User Model
* JWT Authentication
* Role-based Authorization
* School Management
* Academic Terms
* Classes
* Sessions
* Teacher Assignments
* Session Reports
* Education Review Workflow
* Report Approval
* Report Rejection
* Report Resubmission
* Late Submission Detection
* Monthly Teacher Report Summary
* Teacher Term Rates
* Salary Management
* Automated Tests

---

# Testing

To run all project tests:

```bash
python manage.py test
```

The test suite verifies the functionality of the implemented applications and APIs.

---

# Useful Commands

Run server:

```bash
python manage.py runserver
```

Run all tests:

```bash
python manage.py test
```

Run Account tests:

```bash
python manage.py test account
```

Run Finance tests:

```bash
python manage.py test finance
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

Create a user:

```bash
python manage.py create_user
```

---

# Git Workflow

The project uses feature-based branches.

Examples:

```text
feature/user-model
feature/authentication
feature/jwt-tests
feature/account-tests
feature/academic-app
feature/teacher-assignment
test/session-report-edited-at-late
```

Development flow:

```text
Feature Branch
      |
      ↓
Pull Request
      |
      ↓
dev Branch
      |
      ↓
main Branch
```

Completed phases are merged into the main development branch and then released through the main branch.

Version tags are used to identify important project milestones.

---

# Project Architecture

The overall architecture can be summarized as:

```text
                    Final Project
                         |
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
     Account          Academic          Finance
        |                |                |
        ↓                ↓                ↓
 Authentication       School          Session Reports
 Authorization        Terms           Teacher Rates
 User Roles            Classes          Salary
                       Sessions
                       Teacher
                      Assignment
```

The system uses Django REST Framework APIs with JWT authentication and role-based authorization across the different modules.
