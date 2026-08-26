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

Examples:

* End date cannot be before start date.
* Terms cannot overlap.
* A term must start on the first day of a month.
* A term must end on the last day of the same month.

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

Session duration is validated against the supported values defined by the project implementation:

```text
60 minutes
90 minutes
120 minutes
```

---

# Session Management

Sessions represent individual teaching sessions belonging to a class.

A session contains information such as:

* Class
* Session number
* Session date

Sessions are later connected to Session Reports in the Finance module.

The system prevents duplicate session numbers and duplicate session dates within the same classroom.

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

The system validates teacher assignment periods and prevents conflicting assignments for the same classroom during the same period.

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

Late reports are excluded from the salary amount calculation.

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

# Phase 4 - Salary Calculation & Final Financial Workflow

## Goal

The goal of Phase 4 was to complete the financial workflow of the system by calculating teacher salaries based on approved session reports and teacher-specific term rates.

This phase connects the academic and session reporting modules to the final salary calculation process.

The main focus was:

* Defining teacher term rates
* Calculating monthly teacher salaries
* Supporting different session durations
* Handling approved, pending and rejected reports
* Excluding late reports from salary calculation
* Supporting bulk salary calculation
* Providing salary history for teachers
* Providing monthly salary lists for Finance users
* Verifying salary calculations using automated tests

---

# Teacher Term Rate

A `TeacherTermRate` defines the base salary rate of a teacher for a specific academic term.

Relationship:

```text
Teacher
   |
   ↓
Teacher Term Rate
   |
   ↓
Term
```

Each teacher has a separate base rate for each term.

The same teacher and term cannot have more than one active rate.

Example:

```text
Teacher A
Term 1
Base Rate = 200000
```

---

# Salary Calculation

Monthly salary is calculated based on approved session reports and the teacher's term rate.

The supported session durations have different salary multipliers:

```text
60 minutes   → 70% of base rate
90 minutes   → 100% of base rate
120 minutes  → 130% of base rate
```

The calculation is:

```text
60-minute sessions
    → count × base_rate × 0.7

90-minute sessions
    → count × base_rate

120-minute sessions
    → count × base_rate × 1.3
```

---

# Salary Eligibility Rules

Before calculating salary, all reports for the teacher in the target month must be approved.

The system prevents salary calculation when there is:

* A pending report
* A rejected report

In addition, only reports with:

```text
status = approved
is_late = false
```

are included in the salary amount.

Therefore, an approved but late report does not contribute to the calculated wage.

If there are no session reports for the teacher in the target month, salary calculation is also rejected.

---

# Example Salary Calculation

The salary calculation follows the worked example defined in the project specification.

For example:

```text
Base Rate = 200000

10 approved 90-minute sessions
2 approved 60-minute sessions
1 approved 120-minute session
1 late session report
```

The late report is excluded from the calculation.

The salary becomes:

```text
10 × 200000
+
2 × (200000 × 0.7)
+
1 × (200000 × 1.3)

= 2000000
+ 280000
+ 260000

= 2540000
```

Therefore:

```text
calculated_amount = 2540000
final_amount      = 2540000
```

---

# Monthly Salary Calculation

The Finance module provides an endpoint for calculating the monthly salary of a specific teacher.

Endpoint:

```text
POST /api/teacher-monthly-salary/calculate/
```

The request contains:

```text
teacher
year
month
```

The calculation process is:

```text
Teacher
   |
   ↓
Find monthly reports
   |
   ↓
Check all reports are approved
   |
   ↓
Find Teacher Term Rate
   |
   ↓
Select approved and non-late reports
   |
   ↓
Calculate wage by session duration
   |
   ↓
Create / update Salary
```

---

# Bulk Salary Calculation

Finance users can calculate salaries for all teachers who have session reports in a specific month.

Endpoint:

```text
POST /api/teacher-monthly-salary/calculate-all/
```

This operation calculates the salary for each teacher for the requested month.

The calculation uses the same validation and salary rules as individual salary calculation.

---

# Salary List

Finance users can view monthly salary records.

Endpoint:

```text
GET /api/salaries/
```

Salary records contain information such as:

* Teacher
* Term
* Year
* Month
* Calculated amount
* Final amount
* Adjustment reason

---

# Teacher Salary History

Teachers can view their own salary history.

Endpoint:

```text
GET /api/my-salaries/
```

The endpoint only returns salaries belonging to the authenticated teacher.

Teachers cannot access another teacher's salary history.

---

# Financial APIs

The Finance module provides the following endpoints:

```text
POST  /api/teacher-term-rates/
GET   /api/teacher-term-rates/

POST  /api/teacher-monthly-salary/calculate/

POST  /api/teacher-monthly-salary/calculate-all/

GET   /api/salaries/

GET   /api/my-salaries/
```

---

# Phase 4 Testing

Automated tests were added to verify the complete financial workflow.

The tests cover:

* Teacher term rate creation
* Duplicate teacher term rate validation
* Monthly salary calculation
* Salary calculation for 60-minute sessions
* Salary calculation for 90-minute sessions
* Salary calculation for 120-minute sessions
* Worked salary calculation example
* Excluding late reports from salary calculation
* Preventing salary calculation when reports are pending
* Preventing salary calculation when reports are rejected
* Preventing salary calculation when there are no reports for the month
* Verifying calculated amount
* Verifying final amount
* Bulk salary calculation
* Salary list access
* Teacher salary history
* Role-based financial permissions
* End-to-end salary workflow

The end-to-end tests cover the complete flow from academic data creation to final salary calculation.

---

# End-to-End System Workflow

The complete system flow is:

```text
User Creation
      |
      ↓
Authentication
      |
      ↓
School Creation
      |
      ↓
Term Creation
      |
      ↓
Class Creation
      |
      ↓
Teacher Assignment
      |
      ↓
Session Creation
      |
      ↓
Teacher Creates Session Report
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
      |               |
      |               ↓
      |           Teacher Edit
      |               |
      |               ↓
      |            Resubmit
      |               |
      |               ↓
      |            Pending
      |
      ↓
Teacher Term Rate
      |
      ↓
Monthly Salary Calculation
      |
      ↓
Salary Record
      |
      ├───────────────┐
      ↓               ↓
Finance Salary List   Teacher Salary History
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
        |
        ↓
Phase 4
Salary Calculation & Final Financial Workflow
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
* Monthly Salary Calculation
* Bulk Salary Calculation
* Salary Management
* Teacher Salary History
* Finance Salary List
* Automated Tests
* End-to-end salary workflow testing
* GitHub Actions CI

---

# Testing

To run all project tests:

```bash
python manage.py test
```

The test suite verifies the functionality of the implemented applications and APIs.

Run Account tests:

```bash
python manage.py test account
```

Run Finance tests:

```bash
python manage.py test finance
```

Run Academic tests:

```bash
python manage.py test academic
```

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
feature/session-admin
feature/salary-end-to-end-tests
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

---

# Project Completion

Phase 4 completes the main business workflow of the project.

The final system supports the complete process from user and academic data creation to teacher session reporting, report review and approval, teacher-specific term rates, and final monthly salary calculation.

The complete workflow is validated using automated tests and end-to-end financial tests.
