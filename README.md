# RankTutor - Comprehensive Tutor Portal Platform

A full-featured tutor portal platform built with Django 5, Jinja2 templates, Tailwind CSS, Alpine.js, and HTMX.

## Features

### Phase 1: MVP (Completed)
- ✅ User Management System (5 roles: Student, Parent, Tutor, City Admin, Global Admin)
- ✅ Tutor Profile Builder with document verification
- ✅ Advanced Tutor Search (Subject, Level, Mode, Fee, Language)
- ✅ Booking & Scheduling System
- ✅ Payment System with 15% commission model
- ✅ Reviews & Ratings System
- ✅ In-App Messaging
- ✅ City Admin Dashboard
- ✅ Global Admin Dashboard

### Phase 2-4: Enhanced Features (Planned)
- Geolocation & Map-based Search (OpenStreetMap/Leaflet)
- AI Matchmaking
- Calendar Sync (Google/Outlook)
- Video Conferencing (Jitsi/Zoom)
- Premium Features
- Advanced Analytics
- CMS & Marketing
- And much more...

## Technology Stack

- **Backend**: Django 5.0.1
- **Templates**: Jinja2 (primary), Django Templates (admin only)
- **Frontend**: Tailwind CSS, Alpine.js, HTMX
- **Database**: SQLite (dev), PostgreSQL (production)
- **Python**: 3.12

## Installation

1. Clone the repository
2. Create virtual environment:
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create test users:
   ```bash
   python manage.py create_test_users
   ```

6. Create superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

7. Run development server:
   ```bash
   python durga.py
   # Or
   python manage.py runserver
   ```

## Project Structure

```
ranktutor/
├── core/              # Base models and utilities
├── users/             # User authentication and profiles
├── tutors/            # Tutor profiles and management
├── students/          # Student profiles
├── bookings/          # Booking and scheduling
├── payments/          # Payment processing
├── messaging/         # In-app messaging
├── reviews/           # Reviews and ratings
├── admin_panel/       # Admin dashboards
├── cms/               # Content management
├── analytics/         # Analytics and reporting
└── notifications/     # Email and push notifications
```

## User Roles

1. **Student**: Search and book tutors, track lessons
2. **Parent**: Manage bookings for children
3. **Tutor**: Create profile, manage bookings, set pricing
4. **City Admin**: Approve tutors, manage local operations
5. **Global Admin**: Platform-wide management

## Test Users

Test users are created using the management command. See `test_user.txt` for credentials.

## Admin Access

- Django Admin: `/sd/` (Django templates)
- Custom Admin: `/admin/` (Jinja2 templates)

## Development

Use `durga.py` script to clear cache and start the development server:

```bash
python durga.py
```

## Environment Variables

Create a `.env` file (see `.env.example`):

```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
COMMISSION_PERCENTAGE=15
```

## License

This project is proprietary software.

## Support

For issues and questions, please contact the development team.

# ranktutor-25
# ranktutor-25
