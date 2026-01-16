from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .serializers import (
    UserSerializer, TutorProfileSerializer, BookingSerializer,
    PaymentSerializer, ReviewSerializer, AvailabilitySlotSerializer
)
from tutors.models import TutorProfile
from bookings.models import Booking, AvailabilitySlot
from payments.models import Payment
from reviews.models import Review
from django.contrib.auth import get_user_model

User = get_user_model()


class TutorProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for tutor profiles"""
    queryset = TutorProfile.objects.filter(is_verified=True, verification_status='approved')
    serializer_class = TutorProfileSerializer
    permission_classes = [AllowAny]
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Get tutor availability slots"""
        tutor = self.get_object()
        slots = AvailabilitySlot.objects.filter(tutor=tutor.user)
        serializer = AvailabilitySlotSerializer(slots, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get tutor reviews"""
        tutor = self.get_object()
        reviews = Review.objects.filter(tutor=tutor.user, is_approved=True)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    """API endpoint for bookings"""
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_tutor():
            return Booking.objects.filter(tutor=user)
        elif user.is_student() or user.is_parent():
            return Booking.objects.filter(student=user)
        return Booking.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(student=self.request.user)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a booking"""
        booking = self.get_object()
        if booking.tutor != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        booking.status = 'accepted'
        booking.accepted_at = timezone.now()
        booking.save()
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a booking"""
        booking = self.get_object()
        if booking.tutor != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        booking.status = 'rejected'
        booking.save()
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for payments"""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_tutor():
            return Payment.objects.filter(tutor=user)
        elif user.is_student() or user.is_parent():
            return Payment.objects.filter(student=user)
        return Payment.objects.none()


class ReviewViewSet(viewsets.ModelViewSet):
    """API endpoint for reviews"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(is_approved=True)
    
    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class AvailabilitySlotViewSet(viewsets.ModelViewSet):
    """API endpoint for availability slots"""
    serializer_class = AvailabilitySlotSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_tutor():
            return AvailabilitySlot.objects.filter(tutor=self.request.user)
        return AvailabilitySlot.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(tutor=self.request.user)

