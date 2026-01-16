from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import User
from tutors.models import TutorProfile, TutorDocument, Subject
from bookings.models import Booking
from payments.models import Payment
from reviews.models import Review, Dispute, SafetyReport
from core.models import TimeStampedModel


class AdminUserForm(forms.ModelForm):
    """Form for admin to create/edit users"""
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
    }), required=False, help_text='Leave blank to keep current password')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'role', 'is_active', 'is_verified', 'email_verified', 'date_of_birth']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'}),
            'email': forms.EmailInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'}),
            'first_name': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'}),
            'last_name': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'}),
            'phone': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'}),
            'role': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-indigo-600 focus:ring-indigo-500'}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-indigo-600 focus:ring-indigo-500'}),
            'email_verified': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-indigo-600 focus:ring-indigo-500'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500', 'type': 'date'}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class AdminTutorForm(forms.ModelForm):
    """Form for admin to edit tutor profiles"""
    class Meta:
        model = TutorProfile
        fields = ['bio', 'city', 'state', 'pincode', 'is_verified', 'verification_status', 'is_featured', 
                  'years_of_experience', 'is_available_online', 'is_available_home', 'max_travel_distance']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500', 'rows': 4}),
            'city': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'}),
            'state': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'}),
            'pincode': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'}),
            'verification_status': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'}),
            'max_travel_distance': forms.NumberInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-indigo-600 focus:ring-indigo-500'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-indigo-600 focus:ring-indigo-500'}),
            'is_available_online': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-indigo-600 focus:ring-indigo-500'}),
            'is_available_home': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-indigo-600 focus:ring-indigo-500'}),
        }


class DisputeResolutionForm(forms.ModelForm):
    """Form for resolving disputes"""
    class Meta:
        model = Dispute
        fields = ['status', 'resolution']
        widgets = {
            'status': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'}),
            'resolution': forms.Textarea(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500', 'rows': 4}),
        }


class SafetyReportForm(forms.ModelForm):
    """Form for handling safety reports"""
    class Meta:
        model = SafetyReport
        fields = ['status', 'investigation_notes', 'action_taken']
        widgets = {
            'status': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'}),
            'investigation_notes': forms.Textarea(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500', 'rows': 4}),
            'action_taken': forms.Textarea(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500', 'rows': 3}),
        }


class SubjectForm(forms.ModelForm):
    """Form for managing subjects"""
    class Meta:
        model = Subject
        fields = ['name', 'description', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'}),
            'description': forms.Textarea(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'}),
        }

