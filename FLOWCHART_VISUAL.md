# RankTutor - Visual Flowchart (Mermaid Diagrams)

## 🏠 Application Entry Point

```mermaid
graph TD
    A[User Visits Home Page /] --> B{Is Authenticated?}
    B -->|No| C[Register/Login]
    B -->|Yes| D[Role-Based Redirect]
    C --> E[Select Role]
    E --> F[Student/Parent]
    E --> G[Tutor]
    E --> H[Admin]
    D --> I[Student Dashboard]
    D --> J[Tutor Dashboard]
    D --> K[Admin Dashboard]
```

## 👨‍🎓 Student/Parent Flow

```mermaid
graph TD
    A[Student Login] --> B[Student Dashboard]
    B --> C[Search Tutors]
    C --> D[View Tutor Profile]
    D --> E[Create Booking]
    E --> F{Booking Type?}
    F -->|Single| G[One-time Booking]
    F -->|Recurring| H[Weekly/Monthly Booking]
    G --> I[Tutor Accepts]
    H --> I
    I --> J{Accepted?}
    J -->|Yes| K[Make Payment]
    J -->|No| L[Booking Rejected]
    K --> M[Lesson Scheduled]
    M --> N[Attend Lesson]
    N --> O[Tutor Marks Complete]
    O --> P[Leave Review]
    P --> Q[Review Published]
```

## 👨‍🏫 Tutor Flow

```mermaid
graph TD
    A[Tutor Registration] --> B[Profile Builder]
    B --> C[Upload Documents]
    C --> D[Set Pricing]
    D --> E[Set Availability]
    E --> F[Wait for Verification]
    F --> G{City Admin Approves?}
    G -->|Yes| H[Tutor Active]
    G -->|No| I[Pending Status]
    H --> J[Receive Booking Requests]
    J --> K{Accept or Reject?}
    K -->|Accept| L[Student Pays]
    K -->|Reject| M[Booking Rejected]
    L --> N[Conduct Lesson]
    N --> O[Mark Lesson Complete]
    O --> P[Receive Review]
    P --> Q[Earnings Updated]
```

## 🏛️ City Admin Flow

```mermaid
graph TD
    A[City Admin Login] --> B[City Dashboard]
    B --> C[Pending Tutor Verifications]
    C --> D[Review Tutor Profile]
    D --> E[Review Documents]
    E --> F{Approve Tutor?}
    F -->|Yes| G[Tutor Verified]
    F -->|No| H[Request More Info]
    G --> I[Conduct Quality Audit]
    I --> J[Update Quality Score]
    B --> K[Moderate Reviews]
    B --> L[Resolve Disputes]
    B --> M[Handle Safety Reports]
```

## 🌐 Global Admin Flow

```mermaid
graph TD
    A[Global Admin Login] --> B[Global Dashboard]
    B --> C[Platform Statistics]
    B --> D[User Management]
    B --> E[Tutor Management]
    B --> F[Subject Management]
    B --> G[Payment & Commission]
    B --> H[Analytics & Reports]
    B --> I[System Settings]
    C --> J[View Metrics]
    D --> K[Create/Edit Users]
    E --> L[Feature Tutors]
    F --> M[Manage Subjects]
    G --> N[Track Revenue]
    H --> O[Generate Reports]
```

## 💳 Payment Flow

```mermaid
graph TD
    A[Booking Accepted] --> B[Payment Required]
    B --> C[Student Clicks Pay]
    C --> D[Select Payment Method]
    D --> E{Payment Gateway}
    E -->|Stripe| F[Stripe Payment]
    E -->|Razorpay| G[Razorpay Payment]
    F --> H{Payment Success?}
    G --> H
    H -->|Yes| I[Payment Recorded]
    H -->|No| J[Payment Failed]
    I --> K[Commission Calculated 15%]
    K --> L[Invoice Generated]
    L --> M[Tutor Receives Payment]
    J --> N[Retry Payment]
```

## 📋 Complete Booking Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Pending: Student Creates Booking
    Pending --> Accepted: Tutor Accepts
    Pending --> Rejected: Tutor Rejects
    Accepted --> PaymentPending: Payment Required
    PaymentPending --> PaymentCompleted: Payment Success
    PaymentPending --> PaymentFailed: Payment Failed
    PaymentFailed --> PaymentPending: Retry
    PaymentCompleted --> Scheduled: Lesson Scheduled
    Scheduled --> InProgress: Lesson Time
    InProgress --> Completed: Tutor Marks Complete
    Completed --> Reviewed: Student Reviews
    Reviewed --> [*]
    Rejected --> [*]
```

## 🔐 Authentication & Authorization

```mermaid
graph TD
    A[User Request] --> B[RoleBasedAccessMiddleware]
    B --> C{Is Authenticated?}
    C -->|No| D[Redirect to Login]
    C -->|Yes| E{Check Role}
    E -->|Student/Parent| F[Allow: /students/, /bookings/, /tutors/search/]
    E -->|Tutor| G[Allow: /tutors/dashboard/, /bookings/]
    E -->|City Admin| H[Allow: /admin/city/, /admin/tutors/]
    E -->|Global Admin| I[Allow: /admin/global/, All Routes]
    F --> J[Process Request]
    G --> J
    H --> J
    I --> J
    E -->|Unauthorized| K[403 Forbidden]
```

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        A[Web Browser]
        B[Mobile Browser]
    end
    
    subgraph "Application Layer"
        C[Django Application]
        D[URL Routing]
        E[Middleware]
        F[Views]
        G[Models]
    end
    
    subgraph "Data Layer"
        H[(SQLite/PostgreSQL)]
        I[Redis Cache]
    end
    
    subgraph "External Services"
        J[Stripe API]
        K[Razorpay API]
        L[Email SMTP]
        M[OpenStreetMap]
    end
    
    A --> C
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    F --> I
    F --> J
    F --> K
    F --> L
    F --> M
```

## 📊 Data Models Relationship

```mermaid
erDiagram
    User ||--o{ TutorProfile : has
    User ||--o{ Booking : creates
    User ||--o{ Review : writes
    User ||--o{ Payment : makes
    User ||--o{ Message : sends
    
    TutorProfile ||--o{ Booking : receives
    TutorProfile ||--o{ PricingOption : has
    TutorProfile ||--o{ TutorDocument : has
    TutorProfile ||--o{ Review : receives
    
    Booking ||--|| Payment : requires
    Booking ||--o| Review : generates
    Booking ||--o| Lesson : creates
    
    Payment ||--|| Commission : generates
    Payment ||--|| Invoice : generates
    
    Subject ||--o{ TutorProfile : teaches
    Subject ||--o{ Booking : for
```

## 🔄 Recurring Booking Flow

```mermaid
graph TD
    A[Student Creates Recurring Booking] --> B[Parent Booking Created]
    B --> C[Select Pattern]
    C --> D{Daily/Weekly/Monthly?}
    D -->|Daily| E[Create Daily Bookings]
    D -->|Weekly| F[Create Weekly Bookings]
    D -->|Monthly| G[Create Monthly Bookings]
    E --> H[First Booking Accepted]
    F --> H
    G --> H
    H --> I[Payment for First Booking]
    I --> J[Lesson Completed]
    J --> K[Next Booking Activated]
    K --> L{More Bookings?}
    L -->|Yes| I
    L -->|No| M[All Bookings Complete]
```

## 🎯 User Role Permissions Matrix

```mermaid
graph LR
    subgraph "Student/Parent"
        A1[Search Tutors]
        A2[Create Bookings]
        A3[Make Payments]
        A4[Leave Reviews]
        A5[Send Messages]
    end
    
    subgraph "Tutor"
        B1[Create Profile]
        B2[Upload Documents]
        B3[Set Pricing]
        B4[Accept/Reject Bookings]
        B5[Complete Lessons]
    end
    
    subgraph "City Admin"
        C1[Verify Tutors]
        C2[Approve Documents]
        C3[Quality Audits]
        C4[Moderate Reviews]
        C5[Resolve Disputes]
    end
    
    subgraph "Global Admin"
        D1[All Permissions]
        D2[User Management]
        D3[Platform Settings]
        D4[Analytics]
        D5[System Configuration]
    end
```

---

**Note**: These Mermaid diagrams can be rendered in:
- GitHub/GitLab markdown viewers
- VS Code with Mermaid extension
- Online Mermaid editors (mermaid.live)
- Documentation tools (MkDocs, Sphinx with extensions)

