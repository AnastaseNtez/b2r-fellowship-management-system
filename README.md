# Bridge2Rwanda Farms Fellowship Management System (B2R-FMS)

##  Project Overview
The **B2R Farms Fellowship Management System (B2R-FMS)** is a professional-grade Django platform designed to digitize and optimize the Bridge2Rwanda Farms Fellowship Program. 

By managing **109+ university-graduate Fellows** across Rwanda, the system provides a verified data pipeline for tracking agricultural training impact. It bridges the gap between field activities and administrative oversight through real-time analytics and a structured **Mentor-led review workflow**.

---

## Key Features

| Feature Area | Key Functionality | Target User |
| :--- | :--- | :--- |
| **RBAC Security** | Role-Based Access Control via JWT & Session Auth; Automated profile creation via **Django Signals**. | All Users |
| **Activity Lifecycle** | Fellows log training sessions; Mentors review, approve, or request revisions. | Fellows & Mentors |
| **Data Integrity** | Custom Python validators prevent future-dated logs and illogical numeric entries. | System |
| **Analytics Engine** | Real-time performance leaderboards and geographic impact data via REST API. | Admins,  Viewers, Mentors |
| **Reporting** | One-click **CSV Export** for verified impact data and donor reporting. | Coordinators, Mentors, Admins|



---

## 🏗️ The Mentor-Review Workflow (Data Quality Assurance)
To ensure the integrity of reported impact (such as the **398+ farmers reached**), the system implements a strict approval lifecycle:

1. **Submission**: A Fellow logs a session (Topic, Village, Duration, Farmers, Photos).
2. **Review**: The activity appears on the **Mentor Dashboard** with a "Pending" status.
3. **Audit**: The Mentor can **Approve** the record or flag it for **Revision** with specific feedback.
4. **Resubmission**: If flagged, the Fellow sees a "Needs Revision" alert, updates the record, and resubmits for final approval.



---

## 🗺️ API Documentation (RESTful Endpoints)
All API requests (except Login/Register) require a JWT token in the header:  
`Authorization: Bearer <your_token>`

### 🔐 Authentication
* **POST** `/api/auth/register/` - Create a new user account.
* **POST** `/api/auth/login/` - Obtain JWT access & refresh tokens.
* **POST** `/api/auth/logout/` - Blacklist refresh token to end session.
* **POST** `/api/auth/token/refresh/` - Refresh expired access tokens.

### 👨‍🌾 Fellow Management
* **GET** `/api/fellows/` - List all Fellows.
* **POST** `/api/fellows/` - Create a new Fellow record.
* **GET** `/api/fellows/{id}/` - Get specific Fellow details.
* **PUT** `/api/fellows/{id}/` - Update Fellow information.
* **DELETE** `/api/fellows/{id}/` - Deactivate/Delete Fellow.
* **GET** `/api/fellows/{id}/activities/` - Get specific Fellow's log history.
* **GET** `/api/fellows/statistics/` - High-level metrics for Fellow performance.

### 📝 Training Activities & Analytics
* **GET** `/api/activities/` - List all training activities.
* **POST** `/api/activities/logs/` - Log a new training session.
* **GET** `/api/activities/logs/{id}/` - Get details of a specific log.
* **PUT** `/api/activities/logs/{id}/` - Update an activity log.
* **DELETE** `/api/activities/logs/{id}/` - Remove an activity log.
* **GET** `/api/activities/reports/dashboard/` - Summary metrics for dashboard cards.
* **GET** `/api/activities/reports/fellow-performance/` - Leaderboard data (Sum, Count, Avg).
* **GET** `/api/reports/export/csv/` - Export all verified logs to CSV.

---

## 🛠️ Technical Stack
* **Backend**: Django 4.2+ & Django REST Framework (DRF)
* **Auth**: SimpleJWT (Stateless Token Auth)
* **Frontend**: Bootstrap 5, Django Crispy Forms, Chart.js
* **Database**: SQLite (Development) / PostgreSQL (Production: not yet)

---

## 🧪 Testing and Verification

### 1. Web UI Workflow (Manual Testing)
* **Fellow Submission**: Log in as a Fellow. Navigate to **Submit Activity**. Test validation by entering a future date; the system must prevent the save.
* **Mentor Approval**: Log in as a Mentor. Go to the **Mentor Dashboard**, select a "Pending" activity, and **Approve** it. Ensure the global farmer count updates.
* **Revision Loop**: As a Mentor, flag a report as **Needs Revision**. Log in as the Fellow and ensure the feedback is visible in the edit form.


### 2. Credentials for Web view testing: I will delete this part or change credentials before deploying this project online.
1. **Fellow Users**: testfellow@example.com  or test2@example.com
  **Fellow Users password**: User123!
2. **Mentor or coordinator Users**: mentor1@example.com
    **password**: 2025.Mentor!

---

📧 Contact
Developer: Anastase Nteziryayo

Email: anastasentezi@gmail.com

LinkedIn:https://www.linkedin.com/in/anastase-nteziryayo-24147011b/