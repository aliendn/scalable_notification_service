# 📬 Django Notification Service

A scalable and modular notification system in Django that supports:

- 🔔 System Notifications
- ✉️ Email Notifications
- 📱 SMS Notifications
- ⚙️ Notification Preferences (entity-based, dynamic)
- 📘 Template-based messages

---

## 📦 Features

- Multi-channel notification delivery (Email, SMS, System)
- Centralized `Event` model for logging notification triggers
- `NotificationTemplate` support for dynamic content generation
- `NotificationPreference` system to enable/disable channels for different entities (Company, User, etc.)
- Denormalized design (no foreign keys) for flexibility and performance

---

## 🛠️ Setup Instructions

### 1. Clone and Install Dependencies

```bash
git clone <The-repo-url>
cd notification_service
pip install -r requirements.txt
