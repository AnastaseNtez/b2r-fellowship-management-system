# 🌾 Bridge2Rwanda Farms Fellowship Management System (B2R-FMS)

## 📌 Project Overview

The **B2R Farms Fellowship Management System (B2R-FMS)** is a robust, Django-based web platform designed to streamline and centralize the operational management of the B2R Farms Fellowship Program in Rwanda.

This system addresses the critical need to efficiently manage **109+ Fellows** (university graduates stationed across the country), track their daily **training activities** with smallholder farmers, and generate timely **impact reports** for B2R Farms administrators, coordinators, and external donors.

---

## 🎯 Key Features

The system is built as a multi-user application with strict **Role-Based Access Control (RBAC)** to ensure data security and appropriate access levels:

| Feature Area | Key Functionality | Target User |
| :--- | :--- | :--- |
| **User & Auth** | JWT-based authentication; Supports Admin, Coordinator, Fellow, and Viewer roles. | All Users |
| **Fellow Management** | CRUD operations for Fellow profiles; Sector assignment; Status tracking (Active, Completed). | Admin, Coordinator |
| **Activity Logging** | Fellows log daily training sessions (farmers trained, topic, location, photos) via API/Web UI. | Fellow |
| **Geographic Data** | Manages Rwanda's administrative divisions (Province → District → Sector) for assignment and reporting. | Coordinator |
| **Reporting & Analytics** | Dashboard displays real-time key metrics (total farmers reached, sessions conducted); CSV export for impact reports. | Coordinator, Viewer |

---

## 🛠️ Technical Architecture

This project utilizes a modern and scalable technology stack focused on stability and data integrity.

### Technology Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Backend Framework** | **Django 4.2+** | Core Web Framework and ORM |
| **API** | **Django REST Framework (DRF)** | Handles API development and serialization |
| **Authentication** | **JWT (djangorestframework-simplejwt)** | Secure, stateless token-based authentication |
| **Database** | **SQLite**  | Relational data storage |
| **Frontend** | Django Templates, **Bootstrap 5**, **Chart.js** | Administrative web interface and data visualization |

### Core Database Models

The system relies on six core relational models:

1.  `User/UserProfile`
2.  `Province`, `District`, `Sector`
3.  `Fellow`
4.  `TrainingActivity`

---

## 💻 Getting Started

### Prerequisites

* Python 3.9+
* `pip` (Python package installer)
* Git

### Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/AnastaseNtez/b2r-fellowship-management-system.git]
    cd [your-folder-that-contains-this-repository-you-just-cloned]
    ```

2.  **Install Dependencies:**
    > **Note:** For stability, it is strongly recommended to use a virtual environment, even if installing packages globally:
    ```bash
    # (Optional) Create and activate virtual environment
    # python -m venv venv
    # source venv/bin/activate 
    
    # Install required packages using the generated list
    pip install -r requirements.txt
    ```

3.  **Run Migrations:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

4.  **Create Superuser (Admin):**
    ```bash
    python manage.py createsuperuser
    ```

5.  **Run the Server:**
    ```bash
    python manage.py runserver
    ```
    The application will be accessible at `http://127.0.0.1:8000/`.

---

## 🗺️ API Endpoints (Planned)

The system exposes a secure REST API for all operations. All endpoints will require JWT authentication.

| Feature | HTTP Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Authentication** | `POST` | `/api/auth/login/` | Obtain JWT tokens for authenticated users |
| **Fellows** | `GET` | `/api/fellows/` | List all Fellows |
| **Activities** | `POST` | `/api/activities/` | Log a new training session |
| **Reports** | `GET` | `/api/reports/dashboard/` | Retrieve key metrics for the dashboard |

---

## 📅 Project Timeline (5 Weeks)

| Week | Focus Area | Key Deliverable | Status |
| :--- | :--- | :--- | :--- |
| **1** | Setup, Auth & Geographic Models | Authentication + Geographic Data Models | **In Progress** |
| **2** | Fellow Management | Fellow CRUD + APIs | Planned |
| **3** | Activity Logging & UI | Training log system + Basic Web UI | Planned |
| **4** | Analytics & Reports | Dashboard Endpoints + CSV Export | Planned |
| **5** | Testing, Docs & Polish | Complete, Tested, Documented System | Planned |

---

## 📧 Contact

**Developer:** Anastase Nteziryayo
**Email:** anastasentezi@gmail.com
**LinkedIn:** [https://www.linkedin.com/in/anastase-nteziryayo-24147011b/](https://www.linkedin.com/in/anastase-nteziryayo-24147011b/)
