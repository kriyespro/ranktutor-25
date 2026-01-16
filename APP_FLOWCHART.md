# RankTutor Application Flowchart & User Journey

## 📁 Project Structure

```
ranktutor2025/
├── core/                    # Home page, base templates
├── users/                   # Authentication, user profiles
├── tutors/                 # Tutor profiles, search, management
├── students/               # Student profiles, dashboards
├── bookings/              # Booking system, scheduling
├── payments/              # Payment processing, commissions
├── messaging/             # In-app messaging system
├── reviews/               # Reviews, ratings, disputes
├── admin_panel/           # Custom admin dashboards
├── analytics/             # Reports, analytics
├── cms/                   # Content management (blog, FAQ)
├── notifications/         # Email/push notifications
├── api/                   # REST API endpoints
└── templates/             # Jinja2 templates
```

---

## 🔄 Application Flow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        RANKTUTOR PLATFORM                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Home Page (/) │
                    │  - Featured Tutors │
                    │  - Search Form    │
                    └─────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Register   │    │    Login     │    │  Browse      │
│   /users/    │    │  /users/     │    │  Tutors      │
│   register/  │    │   login/     │    │  /tutors/    │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Role-Based       │
                    │  Dashboard        │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Student/   │    │    Tutor     │    │    Admin     │
│   Parent     │    │  Dashboard   │    │  Dashboard   │
│  Dashboard   │    │  /tutors/    │    │  /admin/     │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

## 👥 User Role Journeys

### 1️⃣ STUDENT/PARENT Journey

```
┌─────────────────────────────────────────────────────────────┐
│                    STUDENT/PARENT FLOW                       │
└─────────────────────────────────────────────────────────────┘

START: Home Page (/)
  │
  ├─→ Register/Login
  │   ├─→ /users/register/ (Create account)
  │   └─→ /users/login/ (Login with username/email)
  │
  ├─→ Dashboard Redirect
  │   └─→ /students/dashboard/
  │       ├─→ View Upcoming Bookings
  │       ├─→ View Past Lessons
  │       └─→ View Messages
  │
  ├─→ Search Tutors
  │   └─→ /tutors/search/
  │       ├─→ Filter by: Subject, City, Mode (Online/Home)
  │       ├─→ View Tutor Cards (Rating, Price, Location)
  │       └─→ Click Tutor → /tutors/<id>/
  │
  ├─→ View Tutor Profile
  │   └─→ /tutors/<id>/
  │       ├─→ View: Bio, Education, Experience, Pricing
  │       ├─→ View: Reviews & Ratings
  │       ├─→ View: Availability
  │       └─→ Action: "Book Now" → /bookings/create/<tutor_id>/
  │
  ├─→ Create Booking
  │   └─→ /bookings/create/<tutor_id>/
  │       ├─→ Select: Date, Time, Duration, Mode
  │       ├─→ Choose: Trial Class (Yes/No)
  │       ├─→ Choose: Recurring (Daily/Weekly/Monthly)
  │       ├─→ Add Notes
  │       └─→ Submit → Booking Status: "Pending"
  │
  ├─→ Booking Management
  │   └─→ /bookings/<booking_id>/
  │       ├─→ View Booking Details
  │       ├─→ Wait for Tutor Acceptance
  │       ├─→ If Accepted → Make Payment
  │       │   └─→ /payments/process/<booking_id>/
  │       │       ├─→ Choose Payment Method (Stripe/Razorpay)
  │       │       └─→ Complete Payment
  │       ├─→ Attend Lesson
  │       └─→ After Lesson → Leave Review
  │           └─→ /reviews/create/<booking_id>/
  │
  ├─→ Messaging
  │   └─→ /messages/
  │       ├─→ View Conversations
  │       ├─→ /messages/<conversation_id>/
  │       └─→ Send Messages to Tutor
  │
  ├─→ Reviews & Ratings
  │   └─→ /reviews/create/<booking_id>/
  │       ├─→ Rate: 1-5 Stars
  │       ├─→ Write Review
  │       └─→ Submit (Moderated by Admin)
  │
  └─→ Profile Management
      └─→ /users/profile/
          ├─→ Update Personal Info
          ├─→ Upload Profile Picture
          └─→ Manage Preferences
```

---

### 2️⃣ TUTOR Journey

```
┌─────────────────────────────────────────────────────────────┐
│                       TUTOR FLOW                            │
└─────────────────────────────────────────────────────────────┘

START: Home Page (/)
  │
  ├─→ Register/Login
  │   ├─→ /users/register/ (Select role: Tutor)
  │   └─→ /users/login/
  │
  ├─→ Dashboard Redirect
  │   └─→ /tutors/dashboard/
  │       ├─→ View Pending Bookings
  │       ├─→ View Upcoming Lessons
  │       ├─→ View Earnings
  │       └─→ View Messages
  │
  ├─→ Profile Builder (First Time)
  │   └─→ /tutors/profile-builder/
  │       ├─→ Step 1: Basic Info
  │       │   ├─→ Headline, Bio, City, State
  │       │   ├─→ Education, Experience Summary
  │       │   ├─→ Teaching Style, Achievements
  │       │   └─→ Languages Spoken
  │       ├─→ Step 2: Subjects & Levels
  │       │   ├─→ Select Subjects (Math, Science, etc.)
  │       │   └─→ Select Teaching Levels (Primary, Secondary, etc.)
  │       ├─→ Step 3: Availability
  │       │   ├─→ Online (Yes/No)
  │       │   ├─→ Home Visits (Yes/No)
  │       │   └─→ Service Areas
  │       ├─→ Step 4: Pricing
  │       │   └─→ Set Hourly Rate
  │       └─→ Submit → Status: "Pending Verification"
  │
  ├─→ Document Upload
  │   └─→ /tutors/documents/
  │       ├─→ Upload: Academic Certificates
  │       ├─→ Upload: ID Proof
  │       └─→ Upload: Police Verification
  │       └─→ Status: "Pending Review" by City Admin
  │
  ├─→ Pricing Management
  │   └─→ /tutors/pricing/
  │       ├─→ Create Pricing Options
  │       │   ├─→ Subject
  │       │   ├─→ Mode (Online/Home)
  │       │   ├─→ Level (Primary/Secondary/etc.)
  │       │   └─→ Price per Hour
  │       └─→ Manage Existing Pricing
  │
  ├─→ Availability Management
  │   └─→ /bookings/availability/
  │       ├─→ Set Available Time Slots
  │       └─→ Calendar Sync (Google/Outlook)
  │
  ├─→ Booking Management
  │   └─→ /bookings/<booking_id>/
  │       ├─→ View Booking Request
  │       ├─→ Accept Booking
  │       │   └─→ /bookings/<id>/accept/
  │       │       └─→ Status: "Accepted" → Student can pay
  │       ├─→ Reject Booking
  │       │   └─→ /bookings/<id>/reject/
  │       │       └─→ Status: "Rejected"
  │       └─→ Complete Lesson
  │           └─→ /bookings/<id>/complete/
  │               ├─→ Add Lesson Notes
  │               └─→ Status: "Completed" → Student can review
  │
  ├─→ Messaging
  │   └─→ /messages/
  │       └─→ Communicate with Students
  │
  ├─→ Premium Features (Optional)
  │   └─→ /tutors/premium/
  │       ├─→ Subscribe to Premium
  │       ├─→ Get Featured Listing
  │       └─→ Enhanced Profile Visibility
  │
  └─→ Profile Updates
      └─→ /tutors/profile-builder/
          └─→ Update Profile Anytime
```

---

### 3️⃣ CITY ADMIN Journey

```
┌─────────────────────────────────────────────────────────────┐
│                    CITY ADMIN FLOW                          │
└─────────────────────────────────────────────────────────────┘

START: Login
  │
  ├─→ Dashboard Redirect
  │   └─→ /admin/city/
  │       ├─→ View City Statistics
  │       ├─→ Pending Tutor Verifications
  │       ├─→ Pending Document Reviews
  │       └─→ Recent Bookings
  │
  ├─→ Tutor Verification
  │   └─→ /admin/tutors/
  │       ├─→ View Tutor List
  │       ├─→ Click Tutor → /admin/tutors/<id>/
  │       │   ├─→ Review Profile
  │       │   ├─→ Review Documents
  │       │   └─→ Approve Tutor
  │       │       └─→ /admin/city/tutor/<id>/approve/
  │       │           └─→ Status: "Verified" → Tutor Active
  │
  ├─→ Document Verification
  │   └─→ /admin/documents/
  │       ├─→ View Pending Documents
  │       ├─→ Click Document → Verify
  │       │   └─→ /admin/city/document/<id>/verify/
  │       │       ├─→ Review Document
  │       │       ├─→ Mark as Verified/Rejected
  │       │       └─→ Add Notes
  │
  ├─→ Quality Audits
  │   └─→ /admin/quality-audits/
  │       ├─→ View Tutors Needing Audit
  │       ├─→ Conduct Audit
  │       │   └─→ /admin/quality-audit/<tutor_id>/
  │       │       ├─→ Review Profile Quality
  │       │       ├─→ Check Ratings
  │       │       └─→ Update Quality Score
  │
  ├─→ User Management
  │   └─→ /admin/users/
  │       ├─→ View All Users
  │       ├─→ Filter by Role
  │       ├─→ View User Details
  │       └─→ Edit/Delete Users
  │
  ├─→ Booking Management
  │   └─→ /admin/bookings/
  │       └─→ Monitor City Bookings
  │
  ├─→ Review Management
  │   └─→ /admin/reviews/
  │       ├─→ View All Reviews
  │       ├─→ Moderate Reviews
  │       └─→ Approve/Reject Reviews
  │
  ├─→ Dispute Resolution
  │   └─→ /admin/disputes/
  │       ├─→ View Disputes
  │       ├─→ /admin/disputes/<id>/
  │       └─→ Resolve Disputes
  │
  └─→ Safety Reports
      └─→ /admin/safety-reports/
          ├─→ View Safety Reports
          └─→ Investigate & Take Action
```

---

### 4️⃣ GLOBAL ADMIN Journey

```
┌─────────────────────────────────────────────────────────────┐
│                  GLOBAL ADMIN FLOW                          │
└─────────────────────────────────────────────────────────────┘

START: Login
  │
  ├─→ Dashboard Redirect
  │   └─→ /admin/global/
  │       ├─→ Platform Statistics
  │       │   ├─→ Total Users, Tutors, Bookings
  │       │   ├─→ Total Revenue
  │       │   └─→ Total Commission
  │       ├─→ Quality Metrics
  │       │   ├─→ Tutors Needing Intervention
  │       │   └─→ Low Quality Tutors
  │       └─→ Quick Actions
  │
  ├─→ User Management
  │   └─→ /admin/users/
  │       ├─→ Create Users
  │       ├─→ Edit Users
  │       ├─→ Delete Users
  │       └─→ View User Details
  │
  ├─→ Tutor Management
  │   └─→ /admin/tutors/
  │       ├─→ View All Tutors
  │       ├─→ Edit Tutor Profiles
  │       ├─→ Feature Tutors
  │       └─→ Manage Tutor Status
  │
  ├─→ Subject Management
  │   └─→ /admin/subjects/
  │       ├─→ Create Subjects
  │       ├─→ Edit Subjects
  │       └─→ Delete Subjects
  │
  ├─→ Booking Management
  │   └─→ /admin/bookings/
  │       └─→ View All Platform Bookings
  │
  ├─→ Payment Management
  │   └─→ /admin/payments/
  │       ├─→ View All Payments
  │       ├─→ View Commissions
  │       └─→ Generate Reports
  │
  ├─→ Review Management
  │   └─→ /admin/reviews/
  │       └─→ Moderate All Reviews
  │
  ├─→ Dispute Management
  │   └─→ /admin/disputes/
  │       └─→ Resolve Platform Disputes
  │
  ├─→ Safety Reports
  │   └─→ /admin/safety-reports/
  │       └─→ Handle Safety Issues
  │
  ├─→ Analytics & Reports
  │   └─→ /analytics/
  │       ├─→ View Dashboard
  │       ├─→ Generate Custom Reports
  │       └─→ Revenue Forecasts
  │
  └─→ System Settings
      └─→ /admin/system/settings/
          ├─→ Teaching Levels
          └─→ Platform Configuration
```

---

## 🔄 Complete Booking Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    BOOKING LIFECYCLE                        │
└─────────────────────────────────────────────────────────────┘

1. STUDENT SEARCHES TUTOR
   │
   └─→ /tutors/search/ → Select Tutor → /tutors/<id>/

2. STUDENT CREATES BOOKING
   │
   └─→ /bookings/create/<tutor_id>/
       ├─→ Fill Booking Form
       └─→ Submit
           └─→ Status: "pending"

3. TUTOR RECEIVES NOTIFICATION
   │
   └─→ /tutors/dashboard/ → View Pending Booking

4. TUTOR ACCEPTS/REJECTS
   │
   ├─→ ACCEPT → /bookings/<id>/accept/
   │   └─→ Status: "accepted"
   │       │
   │       └─→ STUDENT PAYS
   │           └─→ /payments/process/<booking_id>/
   │               ├─→ Payment Gateway (Stripe/Razorpay)
   │               ├─→ Payment Status: "completed"
   │               └─→ Commission Calculated (15%)
   │
   └─→ REJECT → /bookings/<id>/reject/
       └─→ Status: "rejected"
           └─→ Student Notified

5. LESSON SCHEDULED
   │
   └─→ Status: "accepted" + Payment: "completed"
       └─→ Lesson Date/Time Confirmed

6. LESSON COMPLETED
   │
   └─→ TUTOR MARKS COMPLETE
       └─→ /bookings/<id>/complete/
           ├─→ Add Lesson Notes
           └─→ Status: "completed"

7. STUDENT LEAVES REVIEW
   │
   └─→ /reviews/create/<booking_id>/
       ├─→ Rate (1-5 stars)
       ├─→ Write Review
       └─→ Submit → Status: "pending_moderation"

8. ADMIN MODERATES REVIEW
   │
   └─→ /admin/reviews/<id>/
       └─→ Approve → Review Published on Tutor Profile
```

---

## 🔐 Authentication & Authorization Flow

```
┌─────────────────────────────────────────────────────────────┐
│              AUTHENTICATION & AUTHORIZATION                  │
└─────────────────────────────────────────────────────────────┘

REQUEST → Middleware (RoleBasedAccessMiddleware)
  │
  ├─→ Check Authentication
  │   └─→ If Not Authenticated → Redirect to /users/login/
  │
  ├─→ Check Role Permissions
  │   ├─→ Student/Parent → Access: /students/, /bookings/, /tutors/search/
  │   ├─→ Tutor → Access: /tutors/dashboard/, /bookings/
  │   ├─→ City Admin → Access: /admin/city/, /admin/tutors/, /admin/documents/
  │   └─→ Global Admin → Access: /admin/global/, All Admin Routes
  │
  └─→ Allow/Deny Access
      ├─→ Allow → Process Request
      └─→ Deny → 403 Forbidden / Redirect to Dashboard
```

---

## 💰 Payment & Commission Flow

```
┌─────────────────────────────────────────────────────────────┐
│              PAYMENT & COMMISSION SYSTEM                     │
└─────────────────────────────────────────────────────────────┘

1. BOOKING ACCEPTED
   │
   └─→ Payment Required

2. STUDENT INITIATES PAYMENT
   │
   └─→ /payments/process/<booking_id>/
       ├─→ Calculate Total Amount
       │   └─→ (Duration × Price per Hour)
       └─→ Redirect to Payment Gateway

3. PAYMENT GATEWAY
   │
   ├─→ Stripe
   │   └─→ Process Payment
   └─→ Razorpay
       └─→ Process Payment

4. PAYMENT SUCCESS
   │
   └─→ Payment Model Created
       ├─→ Status: "completed"
       ├─→ Amount: Total Paid
       └─→ Commission Calculated
           └─→ Commission Model Created
               ├─→ Amount: (Total × 15%)
               └─→ Status: "pending"

5. INVOICE GENERATED
   │
   └─→ Invoice Model Created
       ├─→ Student Receives Invoice
       └─→ Tutor Receives Payment (After Commission)

6. COMMISSION TRACKING
   │
   └─→ /admin/payments/
       └─→ View All Commissions
```

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SYSTEM ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐
│   Browser    │
│  (Frontend)  │
└──────┬───────┘
       │ HTTP/HTTPS
       ▼
┌─────────────────────────────────────────────────────────────┐
│                    DJANGO APPLICATION                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  URL Routing (ranktutor/urls.py)                     │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                      │                                       │
│  ┌───────────────────▼───────────────────────────────────┐  │
│  │  Middleware (Role-Based Access Control)               │  │
│  └───────────────────┬───────────────────────────────────┘  │
│                      │                                       │
│  ┌───────────────────▼───────────────────────────────────┐  │
│  │  Views (Business Logic)                                │  │
│  │  - core/views.py                                       │  │
│  │  - users/views.py                                      │  │
│  │  - tutors/views.py                                     │  │
│  │  - bookings/views.py                                   │  │
│  │  - payments/views.py                                   │  │
│  │  - admin_panel/views.py                                │  │
│  └───────────────────┬───────────────────────────────────┘  │
│                      │                                       │
│  ┌───────────────────▼───────────────────────────────────┐  │
│  │  Models (Database ORM)                                  │  │
│  │  - User, TutorProfile, Booking, Payment, etc.         │  │
│  └───────────────────┬───────────────────────────────────┘  │
└───────────────────────┼───────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SQLite (Development) / PostgreSQL (Production)       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Payment Gateways: Stripe, Razorpay                  │  │
│  │  Email Service: SMTP (Django Email Backend)           │  │
│  │  Maps: OpenStreetMap/Leaflet                          │  │
│  │  Cache: Redis (Optional) / Local Memory               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Features by Role

### Student/Parent
- ✅ Search tutors by subject, location, mode
- ✅ View tutor profiles with ratings
- ✅ Create booking requests (single/recurring)
- ✅ Make payments via Stripe/Razorpay
- ✅ Track upcoming and past lessons
- ✅ Message tutors
- ✅ Leave reviews and ratings
- ✅ Manage profile

### Tutor
- ✅ Create comprehensive profile
- ✅ Upload verification documents
- ✅ Set pricing (per subject/mode/level)
- ✅ Manage availability
- ✅ Accept/reject booking requests
- ✅ Complete lessons and add notes
- ✅ View earnings and commissions
- ✅ Premium features (featured listing)
- ✅ Calendar sync

### City Admin
- ✅ Approve tutor profiles
- ✅ Verify tutor documents
- ✅ Conduct quality audits
- ✅ Manage city-level users
- ✅ Moderate reviews
- ✅ Resolve disputes
- ✅ Handle safety reports

### Global Admin
- ✅ Platform-wide statistics
- ✅ Manage all users and tutors
- ✅ Subject management
- ✅ Payment and commission tracking
- ✅ Analytics and reports
- ✅ System settings
- ✅ Full platform oversight

---

## 📱 URL Structure Summary

```
/                           → Home page (Featured tutors, search)
/users/                     → Authentication
  ├─ register/              → User registration
  ├─ login/                 → User login
  ├─ logout/                → User logout
  └─ profile/               → User profile management

/tutors/                    → Tutor features
  ├─ dashboard/             → Tutor dashboard
  ├─ profile-builder/       → Create/edit tutor profile
  ├─ pricing/               → Manage pricing options
  ├─ documents/             → Upload verification documents
  ├─ search/                → Search tutors
  ├─ become-tutor/          → Information page
  └─ <id>/                  → Tutor detail page

/students/                  → Student features
  └─ dashboard/             → Student dashboard

/bookings/                  → Booking system
  ├─ create/<tutor_id>/     → Create booking request
  ├─ <id>/                  → Booking detail
  ├─ <id>/accept/           → Accept booking (tutor)
  ├─ <id>/reject/           → Reject booking (tutor)
  ├─ <id>/complete/         → Complete lesson (tutor)
  └─ availability/          → Manage availability (tutor)

/payments/                  → Payment system
  ├─ process/<booking_id>/  → Process payment
  └─ history/               → Payment history

/messages/                  → Messaging
  └─ <conversation_id>/     → Conversation detail

/reviews/                   → Reviews
  └─ create/<booking_id>/   → Create review

/admin/                     → Custom admin panel
  ├─ city/                  → City admin dashboard
  ├─ global/                → Global admin dashboard
  ├─ users/                 → User management
  ├─ tutors/                → Tutor management
  ├─ bookings/              → Booking management
  ├─ payments/              → Payment management
  ├─ reviews/               → Review management
  ├─ disputes/              → Dispute management
  ├─ documents/             → Document management
  └─ subjects/              → Subject management

/analytics/                 → Analytics
  ├─ dashboard/             → Analytics dashboard
  └─ reports/               → Custom reports

/sd/                        → Django admin (backup)
```

---

## 🔄 Data Flow Example: Complete Booking Process

```
1. Student visits home page (/)
   ↓
2. Searches for tutor (/tutors/search/?subject=Math&city=Mumbai)
   ↓
3. Views tutor profile (/tutors/123/)
   ↓
4. Clicks "Book Now" → /bookings/create/123/
   ↓
5. Fills booking form:
   - Date: 2025-11-15
   - Time: 14:00
   - Duration: 2 hours
   - Mode: Online
   - Recurring: Weekly
   ↓
6. Submits → Booking created (status: "pending")
   ↓
7. Tutor receives notification
   ↓
8. Tutor views booking → /bookings/456/
   ↓
9. Tutor accepts → /bookings/456/accept/
   ↓
10. Booking status: "accepted"
    ↓
11. Student redirected to payment → /payments/process/456/
    ↓
12. Payment processed via Stripe/Razorpay
    ↓
13. Payment status: "completed"
    ↓
14. Commission calculated (15% of payment)
    ↓
15. Lesson scheduled for 2025-11-15 at 14:00
    ↓
16. On lesson day, tutor marks complete → /bookings/456/complete/
    ↓
17. Booking status: "completed"
    ↓
18. Student can leave review → /reviews/create/456/
    ↓
19. Review submitted (status: "pending_moderation")
    ↓
20. Admin moderates review → /admin/reviews/789/
    ↓
21. Review approved → Published on tutor profile
    ↓
22. Recurring booking created for next week (2025-11-22)
    ↓
23. Process repeats for recurring bookings
```

---

## 🛠️ Technology Stack

- **Backend**: Django 5.0.1 (Python 3.12)
- **Templates**: Jinja2 (Primary), Django Templates (Admin)
- **Frontend**: Tailwind CSS, Alpine.js, HTMX
- **Database**: SQLite (Dev), PostgreSQL (Prod)
- **Cache**: Redis (Optional) / Local Memory
- **Payments**: Stripe, Razorpay
- **Maps**: OpenStreetMap/Leaflet
- **API**: Django REST Framework
- **PWA**: Service Worker, Manifest

---

## 📝 Notes

- All templates use Jinja2 syntax (`.jinja` extension)
- Django admin available at `/sd/` as backup
- Custom admin panel at `/admin/` with full functionality
- Role-based access control enforced via middleware
- Commission fixed at 15% (configurable in settings)
- Recurring bookings supported (daily/weekly/monthly)
- Review moderation required before publication
- Document verification required for tutor approval

---

**Generated**: November 12, 2025
**Version**: 1.0
**Project**: RankTutor Platform

