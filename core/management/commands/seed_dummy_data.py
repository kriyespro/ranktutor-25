from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from bookings.models import AvailabilitySlot, Booking, CalendarSync, Lesson
from messaging.models import Conversation, Message
from payments.models import Commission, Invoice, Payment, PremiumPayment
from reviews.models import ContentModeration, Dispute, Review, SafetyReport
from tutors.models import (
    PricingOption,
    QualityAudit,
    QualityCertification,
    Subject,
    TutorDocument,
    TutorProfile,
)


class Command(BaseCommand):
    help = "Seed the database with comprehensive dummy data for demos and development."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Seeding dummy data..."))

        with transaction.atomic():
            users = self._create_users()
            subjects = self._create_subjects()
            tutor_profiles = self._create_tutors(users, subjects)
            bookings = self._create_bookings(users, subjects, tutor_profiles)
            self._create_lessons(bookings)
            self._create_payments(bookings, users)
            self._create_quality_records(tutor_profiles, users)
            self._create_messaging(users, bookings)
            self._create_reviews_and_reports(users, bookings)
            self._create_calendar_syncs(users)

        self.stdout.write(self.style.SUCCESS("Dummy data seeded successfully!"))

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------

    def _create_users(self):
        User = get_user_model()

        user_specs = [
            {
                "key": "global_admin",
                "username": "demo_global_admin",
                "email": "global.admin@demo.local",
                "role": "global_admin",
                "first_name": "Global",
                "last_name": "Admin",
            },
            {
                "key": "city_admin",
                "username": "demo_city_admin",
                "email": "city.admin@demo.local",
                "role": "city_admin",
                "first_name": "City",
                "last_name": "Manager",
            },
            {
                "key": "tutor_one",
                "username": "demo_tutor_one",
                "email": "tutor.one@demo.local",
                "role": "tutor",
                "first_name": "Anita",
                "last_name": "Verma",
            },
            {
                "key": "tutor_two",
                "username": "demo_tutor_two",
                "email": "tutor.two@demo.local",
                "role": "tutor",
                "first_name": "Rahul",
                "last_name": "Tiwari",
            },
            {
                "key": "student_one",
                "username": "demo_student_one",
                "email": "student.one@demo.local",
                "role": "student",
                "first_name": "Priya",
                "last_name": "Sharma",
            },
            {
                "key": "student_two",
                "username": "demo_student_two",
                "email": "student.two@demo.local",
                "role": "student",
                "first_name": "Arjun",
                "last_name": "Patel",
            },
            {
                "key": "parent_user",
                "username": "demo_parent",
                "email": "parent@demo.local",
                "role": "parent",
                "first_name": "Meera",
                "last_name": "Khanna",
            },
        ]

        users = {}
        default_password = "DemoPass123!"

        for spec in user_specs:
            user, created = User.objects.get_or_create(
                username=spec["username"],
                defaults={
                    "email": spec["email"],
                    "role": spec["role"],
                    "first_name": spec["first_name"],
                    "last_name": spec["last_name"],
                    "is_active": True,
                    "email_verified": True,
                },
            )

            if created:
                user.set_password(default_password)
                user.save(update_fields=["password"])

            # Ensure base attributes are up to date
            update_fields = []
            for field in ["email", "role", "first_name", "last_name"]:
                if getattr(user, field) != spec[field]:
                    setattr(user, field, spec[field])
                    update_fields.append(field)

            if update_fields:
                user.save(update_fields=update_fields)

            users[spec["key"]] = user

        self.stdout.write(self.style.SUCCESS("Users ready."))
        return users

    def _create_subjects(self):
        subject_specs = [
            ("Mathematics", "Algebra, Calculus, Geometry and more"),
            ("Physics", "Mechanics, Thermodynamics and modern physics"),
            ("Chemistry", "Organic, Inorganic and Physical chemistry"),
            ("English", "Literature, Grammar and Communication"),
        ]

        subjects = []
        for name, description in subject_specs:
            subject, _ = Subject.objects.get_or_create(
                name=name, defaults={"description": description}
            )
            subjects.append(subject)

        self.stdout.write(self.style.SUCCESS("Subjects ready."))
        return subjects

    def _create_tutors(self, users, subjects):
        tutor_profiles = []
        admin_user = users["global_admin"]

        tutor_payloads = [
            {
                "user": users["tutor_one"],
                "headline": "IIT graduate • IIT-JEE mentor • Calculus expert",
                "bio": "Experienced Math tutor with 8+ years helping students excel in competitive exams.",
                "education": "B.Tech in Mechanical Engineering, IIT Bombay\nCertified Advanced Calculus Trainer",
                "experience_summary": "Worked with over 200 students for IIT-JEE and Olympiad preparation. Former faculty at a leading test prep institute.",
                "teaching_style": "Concept-first approach with live problem solving, diagnostic assessments, and personalised study plans.",
                "achievements": "98% of students score above 90 percentile in IIT-JEE Maths.\nFeatured speaker at National STEM Educators Summit 2024.",
                "languages": "English, Hindi",
                "hourly_rate": Decimal("1200.00"),
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                "is_verified": True,
                "verification_status": "approved",
                "subjects": subjects[:2],  # Math, Physics
                "teaching_levels": "senior_secondary",
                "years_of_experience": 8,
                "average_rating": Decimal("4.7"),
                "total_reviews": 24,
                "is_available_online": True,
                "is_available_home": True,
                "max_travel_distance": 10,
                "service_areas": "South Mumbai, Navi Mumbai",
            },
            {
                "user": users["tutor_two"],
                "headline": "IELTS Band 9 scorer • British Council certified",
                "bio": "Language and communication trainer specialising in IELTS and TOEFL preparation.",
                "education": "MA in English Literature, Christ University\nBritish Council Certified IELTS Trainer",
                "experience_summary": "Trained professionals and students across 7 countries. Former corporate communication coach at a Fortune 500 company.",
                "teaching_style": "Interactive sessions with role-play, personalised feedback recordings, and vocabulary sprints.",
                "achievements": "Helped 150+ students achieve IELTS Band 7 and above.\nPublished author in international language journals.",
                "languages": "English, Hindi, Kannada",
                "hourly_rate": Decimal("1400.00"),
                "city": "Bengaluru",
                "state": "Karnataka",
                "pincode": "560001",
                "is_verified": False,
                "verification_status": "under_review",
                "subjects": subjects[2:],  # Chemistry, English
                "teaching_levels": "graduate",
                "years_of_experience": 5,
                "average_rating": Decimal("4.3"),
                "total_reviews": 12,
                "is_available_online": True,
                "is_available_home": False,
                "max_travel_distance": 0,
                "service_areas": "Koramangala, Indiranagar",
            },
        ]

        for payload in tutor_payloads:
            profile, created = TutorProfile.objects.get_or_create(
                user=payload["user"],
                defaults={
                    "bio": payload["bio"],
                    "city": payload["city"],
                    "state": payload["state"],
                    "pincode": payload["pincode"],
                },
            )

            for field in [
                "bio",
                "headline",
                "education",
                "experience_summary",
                "teaching_style",
                "achievements",
                "languages",
                "hourly_rate",
                "city",
                "state",
                "pincode",
                "is_verified",
                "verification_status",
                "teaching_levels",
                "years_of_experience",
                "average_rating",
                "total_reviews",
                "is_available_online",
                "is_available_home",
                "max_travel_distance",
                "service_areas",
            ]:
                setattr(profile, field, payload[field])

            profile.profile_complete = True
            profile.has_academic_verification = payload["is_verified"]
            profile.last_quality_audit = timezone.now() - timedelta(days=7)
            profile.quality_score = Decimal("82.5")
            profile.save()
            profile.subjects.set(payload["subjects"])

            tutor_profiles.append(profile)

            # Availability slots
            AvailabilitySlot.objects.get_or_create(
                tutor=payload["user"],
                day_of_week=0,
                start_time=timezone.datetime.strptime("16:00", "%H:%M").time(),
                end_time=timezone.datetime.strptime("18:00", "%H:%M").time(),
            )
            AvailabilitySlot.objects.get_or_create(
                tutor=payload["user"],
                day_of_week=2,
                start_time=timezone.datetime.strptime("10:00", "%H:%M").time(),
                end_time=timezone.datetime.strptime("13:00", "%H:%M").time(),
            )

            # Pricing options
            PricingOption.objects.get_or_create(
                tutor=profile,
                subject=payload["subjects"][0],
                mode="online",
                level="senior_secondary",
                defaults={"price_per_hour": Decimal("1200.00")},
            )
            PricingOption.objects.get_or_create(
                tutor=profile,
                subject=payload["subjects"][-1],
                mode="home",
                level="secondary",
                defaults={"price_per_hour": Decimal("1500.00")},
            )

            # Tutor documents (simple text content)
            if not profile.documents.exists():
                document = TutorDocument(
                    tutor=profile,
                    document_type="id_proof",
                    is_verified=payload["is_verified"],
                    verified_by=admin_user if payload["is_verified"] else None,
                    verified_at=timezone.now() if payload["is_verified"] else None,
                    notes="Sample ID proof submitted during demo seeding.",
                )
                document.document_file.save(
                    f"{profile.user.username}_id_proof.txt",
                    ContentFile("Sample ID proof content."),
                    save=True,
                )

        self.stdout.write(self.style.SUCCESS("Tutor profiles ready."))
        return tutor_profiles

    def _create_bookings(self, users, subjects, tutor_profiles):
        bookings = []
        now = timezone.now()
        student_users = [users["student_one"], users["student_two"]]

        booking_specs = [
            {
                "student": student_users[0],
                "tutor": tutor_profiles[0].user,
                "subject": subjects[0],
                "mode": "online",
                "lesson_date": (now + timedelta(days=3)).date(),
                "lesson_time": (now + timedelta(hours=48)).time().replace(microsecond=0),
                "duration_hours": Decimal("1.5"),
                "price_per_hour": Decimal("1200.00"),
                "status": "completed",
                "student_notes": "Focus on calculus revision for upcoming test.",
            },
            {
                "student": student_users[1],
                "tutor": tutor_profiles[1].user,
                "subject": subjects[3],
                "mode": "home",
                "lesson_date": (now + timedelta(days=5)).date(),
                "lesson_time": (now + timedelta(hours=72)).time().replace(microsecond=0),
                "duration_hours": Decimal("2.0"),
                "price_per_hour": Decimal("1400.00"),
                "status": "accepted",
                "address": "742 Evergreen Terrace",
                "city": "Bengaluru",
                "pincode": "560034",
                "student_notes": "Spoken English and IELTS speaking practice.",
            },
        ]

        for spec in booking_specs:
            booking, created = Booking.objects.get_or_create(
                student=spec["student"],
                tutor=spec["tutor"],
                subject=spec["subject"],
                lesson_date=spec["lesson_date"],
                lesson_time=spec["lesson_time"],
                defaults={
                    "mode": spec["mode"],
                    "duration_hours": spec["duration_hours"],
                    "price_per_hour": spec["price_per_hour"],
                    "status": spec["status"],
                    "address": spec.get("address", ""),
                    "city": spec.get("city", ""),
                    "pincode": spec.get("pincode", ""),
                    "student_notes": spec.get("student_notes", ""),
                    "tutor_notes": "Prepared lesson plan and resources.",
                    "is_trial": False,
                    "trial_is_free": False,
                    "accepted_at": timezone.now(),
                    "completed_at": timezone.now()
                    if spec["status"] == "completed"
                    else None,
                },
            )

            if not created:
                for field, value in {
                    "mode": spec["mode"],
                    "duration_hours": spec["duration_hours"],
                    "price_per_hour": spec["price_per_hour"],
                    "status": spec["status"],
                    "address": spec.get("address", ""),
                    "city": spec.get("city", ""),
                    "pincode": spec.get("pincode", ""),
                    "student_notes": spec.get("student_notes", ""),
                }.items():
                    setattr(booking, field, value)
                booking.save()

            bookings.append(booking)

        self.stdout.write(self.style.SUCCESS("Bookings ready."))
        return bookings

    def _create_lessons(self, bookings):
        for booking in bookings:
            Lesson.objects.get_or_create(
                booking=booking,
                defaults={
                    "topics_covered": "Introduction, concept explanation and practice problems.",
                    "homework_assigned": "Complete worksheet #3 and review chapter summary.",
                    "student_progress": "Student is showing consistent improvement.",
                    "student_attended": True,
                    "tutor_attended": True,
                    "is_completed": booking.status == "completed",
                    "completed_at": timezone.now(),
                },
            )

    def _create_payments(self, bookings, users):
        admin_user = users["global_admin"]

        for booking in bookings:
            amount = Decimal(booking.total_amount)
            commission_amount = Decimal(booking.commission_amount)
            tutor_amount = amount - commission_amount

            payment, _ = Payment.objects.get_or_create(
                booking=booking,
                defaults={
                    "student": booking.student,
                    "tutor": booking.tutor,
                    "amount": amount,
                    "commission_amount": commission_amount,
                    "tutor_payout": tutor_amount,
                    "status": "completed",
                    "payment_method": "razorpay",
                    "transaction_id": f"TXN{booking.id:05d}",
                    "payment_gateway_response": {"status": "success"},
                    "paid_at": timezone.now(),
                },
            )

            Invoice.objects.get_or_create(
                payment=payment,
                defaults={"invoice_number": f"INV-{booking.id:05d}"},
            )

            Commission.objects.get_or_create(
                payment=payment,
                defaults={
                    "amount": commission_amount,
                    "percentage": Decimal("15.00"),
                    "is_paid_to_platform": True,
                    "paid_at": timezone.now(),
                },
            )

        # Premium payment for tutor upgrade
        PremiumPayment.objects.get_or_create(
            user=users["tutor_one"],
            payment_type="boost",
            defaults={
                "amount": Decimal("2999.00"),
                "status": "completed",
                "transaction_id": "PRMBOOST001",
            },
        )

        self.stdout.write(self.style.SUCCESS("Payments ready."))

    def _create_quality_records(self, tutor_profiles, users):
        admin_user = users["global_admin"]
        now = timezone.now()

        for profile in tutor_profiles:
            QualityAudit.objects.get_or_create(
                tutor=profile,
                audit_type="manual",
                defaults={
                    "quality_score": Decimal("85.00"),
                    "issues_found": "No major issues. Recommend regular progress reports.",
                    "recommendations": "Continue with current teaching strategy.",
                    "audited_by": admin_user,
                    "is_resolved": True,
                },
            )

            QualityCertification.objects.get_or_create(
                tutor=profile,
                certification_type="verified",
                defaults={
                    "issued_by": admin_user,
                    "valid_until": now + timedelta(days=180),
                    "is_active": True,
                },
            )

    def _create_messaging(self, users, bookings):
        student = users["student_one"]
        tutor = bookings[0].tutor

        conversation, _ = Conversation.objects.get_or_create(
            participant1=student,
            participant2=tutor,
            defaults={"booking": bookings[0], "contact_revealed": True},
        )

        Message.objects.get_or_create(
            conversation=conversation,
            sender=student,
            content="Hi! Looking forward to our calculus session. Can we revise integration first?",
        )
        Message.objects.get_or_create(
            conversation=conversation,
            sender=tutor,
            content="Absolutely! I'll prepare examples focused on integration techniques.",
        )

        self.stdout.write(self.style.SUCCESS("Messaging data ready."))

    def _create_reviews_and_reports(self, users, bookings):
        admin_user = users["global_admin"]
        city_admin = users["city_admin"]

        review_booking = bookings[0]
        Review.objects.get_or_create(
            booking=review_booking,
            student=review_booking.student,
            tutor=review_booking.tutor,
            defaults={
                "rating": 5,
                "comment": "Great explanation of difficult concepts. Very patient and helpful!",
                "is_approved": True,
                "moderated_by": admin_user,
            },
        )

        Dispute.objects.get_or_create(
            booking=bookings[1],
            raised_by=bookings[1].student,
            defaults={
                "dispute_type": "service",
                "description": "Requested clarification on session schedule.",
                "status": "resolved",
                "resolution": "Tutor provided additional clarification and rescheduled lesson.",
                "resolved_by": city_admin,
                "resolved_at": timezone.now(),
            },
        )

        SafetyReport.objects.get_or_create(
            reported_by=bookings[1].student,
            reported_user=bookings[1].tutor,
            defaults={
                "report_type": "other",
                "description": "No real issue. Generated for demo purposes only.",
                "status": "resolved",
                "investigated_by": admin_user,
                "investigation_notes": "Reviewed chat history. No safety concern found.",
                "action_taken": "Educated both parties about community guidelines.",
            },
        )

        ContentModeration.objects.get_or_create(
            content_type="review",
            content_id=review_booking.id,
            defaults={
                "flagged_by": users["city_admin"],
                "reason": "Demo flag for moderation workflow.",
                "is_resolved": True,
                "resolved_by": admin_user,
            },
        )

        self.stdout.write(self.style.SUCCESS("Reviews, disputes and safety reports ready."))

    def _create_calendar_syncs(self, users):
        tutor = users["tutor_one"]
        CalendarSync.objects.get_or_create(
            user=tutor,
            calendar_type="google",
            defaults={
                "calendar_id": "demo.calendar@gmail.com",
                "sync_token": "dummy-sync-token",
                "is_active": True,
                "last_synced_at": timezone.now(),
            },
        )

        self.stdout.write(self.style.SUCCESS("Calendar sync data ready."))

