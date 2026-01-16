from rest_framework import serializers
from django.contrib.auth import get_user_model
from tutors.models import TutorProfile, Subject, PricingOption
from bookings.models import Booking, Lesson, AvailabilitySlot
from payments.models import Payment
from reviews.models import Review
from students.models import StudentProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']
        read_only_fields = ['id']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'description']


class TutorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    subjects = SubjectSerializer(many=True, read_only=True)
    
    class Meta:
        model = TutorProfile
        fields = [
            'id', 'user', 'bio', 'city', 'state', 'pincode',
            'is_available_online', 'is_available_home',
            'average_rating', 'total_reviews', 'quality_score',
            'is_verified', 'subjects'
        ]


class BookingSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    tutor = UserSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'student', 'tutor', 'subject', 'lesson_date',
            'lesson_time', 'duration_hours', 'status', 'mode',
            'total_amount', 'is_recurring'
        ]


class PaymentSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'booking', 'amount', 'status',
            'payment_method', 'created_at', 'paid_at'
        ]


class ReviewSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    tutor = UserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'student', 'tutor', 'rating', 'comment',
            'is_approved', 'created_at'
        ]


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailabilitySlot
        fields = [
            'id', 'day_of_week', 'start_time', 'end_time', 'is_available'
        ]

