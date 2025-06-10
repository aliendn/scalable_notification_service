
# 📬 Scalable Notification Service – Data Model Overview

This project is a modular, scalable, and real-time notification system built with Django and Django Channels. It supports multiple notification channels like Email, SMS, and in-system (WebSocket) alerts. The design is optimized for high-performance enterprise use cases, including camera activity tracking, user management, and company hierarchy operations.

---

## 🧭 Table of Contents

- [✨ Highlights](#-highlights)  
- [🏗 Architecture](#-architecture)  
- [📦 App Breakdown](#-app-breakdown)  
  - [📹 Camera App](#-camera-app)  
  - [🔔 Notification Service App](#-notification-service-app)  
  - [👥 Users App](#-users-app)  
- [🔍 Notification Service Deep Dive](#-notification-service-deep-dive)  
- [⚙️ Utilities & Infrastructure](#️-utilities--infrastructure)  
- [🚀 Setup & Run](#-setup--run)  
- [📚 API Documentation](#-api-documentation)  
- [📈 Performance & Monitoring](#-performance--monitoring)  
- [🛡️ Security](#️-security)  
- [⚡ Performance Optimization](#-performance-optimization)  
- [🧰 Tech Stack](#-tech-stack)  

---

## ✨ Highlights

- Real-time WebSocket-based notifications  
- Modular preference-based delivery (Email/SMS/System)  
- Unified, reusable notification models and APIs  
- Optimized endpoints using batching and streaming  
- Background task handling with Celery  
- API schema generation via `drf-spectacular` & `drf-yasg`  
- JWT-authenticated WebSockets  

---

## 🏗 Architecture

```
├── apps/
│   ├── camera/
│   ├── notification_service/
│   └── users/
├── scalable_notification_service/  # Django project settings & ASGI
├── utils/                          # Shared utilities & mixins
├── manage.py
└── README.md
```

---

## 📦 App Breakdown

### 📹 Camera App

**Handles all camera-related features:**

#### Models
- **Camera**: Stores camera details and statuses  
- **CameraActionLog**: Logs all camera actions with metadata  

#### Views
- `CameraViewSet`:  
  - Create cameras  
  - Toggle online/offline  
  - Move camera  
  - Start/stop recordings  
- `CameraActionLogViewSet`: Read-only logs access  

#### Utilities
- `log_camera_event_and_notify`: Logs events and sends real-time WebSocket alerts to company managers  

#### Management Commands
- `generate_test_data.py`: Populates test users, cameras, logs for development  

---

### 🔔 Notification Service App

**Core of the notification system**

#### Models
- `BaseNotificationModel` (abstract):  
  Fields: `title`, `description`, `priority`, `is_viewed`, `event`, etc.  
- Inherited Models:  
  - `SystemNotification`  
  - `EmailNotification`  
  - `SMSNotification`  
- `Event`: Generic container for event metadata  

#### Features
- Unified notification model with multiple delivery methods  
- Tracks viewed status, soft-deletions, and priorities  
- Role-based and preference-based filtering  
- Efficient querying via `bulk_create`, indexes, and streaming  

#### Views & APIs
- List, detail, and bulk delete notification APIs  
- `NotificationsListView`: supports streamed JSON response  

#### WebSocket
- `NotificationConsumer`: Sends real-time alerts  
- `JWTAuthMiddleware`: Authenticates users via query param token  
- Signals on `post_save`: Push notifications to managers if conditions match  

---

### 👥 Users App

**User registration, authentication, company management, and roles**

#### Authentication
- `UserSerializer`: Uses email as username  
- `UserRegistrationView`: Registers new users and returns JWT tokens  

#### Company & Roles
- `Company`: Business entity  
- `CompanyUser`: Links users to companies with roles (`MANAGER`, `EMPLOYEE`, `CUSTOMER`)  
- Managers are auto-assigned on company creation  

#### Views
- `CompanyViewSet`: CRUD for companies (manager-only)  
- `CompanyUserViewSet`: Manages user roles and memberships  
- `CustomerCreateViewSet`: Adds CUSTOMERS and notifies all managers  
- `UserViewSet`: Read-only listing of active users  

#### Permissions
- `IsCompanyManager`, `IsCompanyEmployee`, `IsCompanyCustomer`, etc.  

#### Flow
1. User registers and gets JWT tokens  
2. Creates company → becomes MANAGER  
3. Adds employees/customers  
4. Employees create CUSTOMERS → manager gets WebSocket notification  
5. Logic prevents last manager removal and self-removal  

---

## 🔍 Notification Service Deep Dive

### Models Overview

```python
class BaseNotificationModel(BaseModel):
    title: str
    description: str
    type_notification: Enum[int]
    priority: Enum[int]
    is_type_enabled: bool
    is_viewed: bool
    is_deleted: bool
    timestamp: datetime
    event: FK → Event
```

#### Inheriting Models
- `SystemNotification`: In-app alerts  
- `EmailNotification`: Includes email field  
- `SMSNotification`: Includes phone number field  

### WebSocket Integration

- **Consumer**: `NotificationConsumer`, group: `notifications_managers`  
- **Middleware**: `JWTAuthMiddleware` for token-based auth  
- **Signal Handler**: Role/type/priority-based push logic  

```json
{
  "type": "notification",
  "id": "...",
  "title": "...",
  "description": "...",
  "priority": 2,
  "timestamp": "2025-06-09T12:34:56.789Z"
}
```

### Delivery Logic
- Managers always receive alerts  
- Employees receive only allowed alert types  
- Respects `is_type_enabled` preferences  

---

## ⚙️ Utilities & Infrastructure

- `JWTAuthMiddleware`: WebSocket JWT auth  
- `BaseAdmin`: Custom admin cleanup  
- `stopwatch`: Decorator for execution time logging  
- Model mixins for UUIDs and timestamps  

---

## 🚀 Setup & Run

```bash
git clone <repo>
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver                      # HTTP server
celery -A scalable_notification_service.celery worker -l info  # Background tasks
daphne scalable_notification_service.asgi:application           # WebSocket server
```

### WebSocket Connection

```ruby
wss://<host>/ws/notifications/?token=<JWT>
```

---

## 📚 API Documentation

- **Swagger**: `/swagger/`  
- **Redoc**: `/redoc/`  
- **OpenAPI Schema**: `/api/schema/`  

---

## 📈 Performance & Monitoring

- `StreamingHttpResponse` for large data  
- Efficient DB access using `.select_related`, `.only()`, `.values()`  
- Profiling with `django-silk`  
- Execution time logging with `stopwatch`  

---

## 🛡️ Security

- Secrets in `.env`  
- JWT tokens for REST & WebSocket  
- HTTPS enforced in production  
- CORS configured  
- DRF-based permission classes  

---

## ⚡ Performance Optimization

### Before
- Full ORM queries  
- DRF serializers for each object  
- High memory usage  

### Now
- Use `.values()` for dicts  
- Skip serializers  
- Use `StreamingHttpResponse`  

**Benefits**:
- Reduced memory  
- Faster responses  
- Immediate delivery  

---

## 🧰 Tech Stack

- Django & Django REST Framework  
- Django Channels  
- Celery  
- drf-spectacular / drf-yasg  
- PostgreSQL  
- Redis (optional for Channels)  

---
