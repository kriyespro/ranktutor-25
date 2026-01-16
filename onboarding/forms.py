from django import forms
from .models import OnboardingData


class RoleSelectionForm(forms.Form):
    """Form for role selection"""
    role = forms.ChoiceField(
        choices=[
            ('student', 'Student'),
            ('tutor', 'Tutor'),
            ('city_admin', 'City Partner'),
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'role-radio'
        }),
        required=True,
        label='आप कौन हैं?'
    )


class StudentOnboardingForm(forms.ModelForm):
    """3-field form for Student onboarding"""
    class_level = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'placeholder': 'e.g., Class 10, Grade 12'
        }),
        label='Class'
    )
    subject = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'placeholder': 'e.g., Mathematics, Science'
        }),
        label='Subject'
    )
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'placeholder': 'e.g., Mumbai, Delhi'
        }),
        label='City'
    )
    location = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'placeholder': 'e.g., Andheri, Connaught Place'
        }),
        label='Location'
    )
    
    class Meta:
        model = OnboardingData
        fields = ['class_level', 'subject', 'city', 'location']


class TutorOnboardingForm(forms.ModelForm):
    """3-field form for Tutor onboarding"""
    subjects = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'placeholder': 'e.g., Mathematics, Physics, Chemistry (comma separated)'
        }),
        label='Subjects',
        help_text='Enter multiple subjects separated by commas'
    )
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'placeholder': 'e.g., Mumbai, Delhi'
        }),
        label='City'
    )
    per_class_fees = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'placeholder': 'e.g., 500, 1000',
            'min': '0',
            'step': '50'
        }),
        label='Per Class Fees (₹)'
    )
    location = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'placeholder': 'e.g., Andheri, Connaught Place'
        }),
        label='Location'
    )
    
    class Meta:
        model = OnboardingData
        fields = ['subjects', 'city', 'per_class_fees', 'location']
    
    def clean_subjects(self):
        """Convert comma-separated subjects to list"""
        subjects_str = self.cleaned_data.get('subjects', '')
        subjects_list = [s.strip() for s in subjects_str.split(',') if s.strip()]
        if not subjects_list:
            raise forms.ValidationError("Please enter at least one subject.")
        return subjects_list
    
    def save(self, commit=True):
        """Save form and convert subjects to list"""
        instance = super().save(commit=False)
        if 'subjects' in self.cleaned_data:
            instance.subjects = self.cleaned_data['subjects']
        if commit:
            instance.save()
        return instance


class CityAdminOnboardingForm(forms.ModelForm):
    """3-field form for City Admin onboarding"""
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'placeholder': 'e.g., Mumbai, Delhi'
        }),
        label='City'
    )
    team_size = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'placeholder': 'e.g., 5, 10',
            'min': '1'
        }),
        label='Team Size'
    )
    contact = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'placeholder': 'e.g., +91 9876543210'
        }),
        label='Contact'
    )
    location = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            'placeholder': 'e.g., Main Office Location'
        }),
        label='Location'
    )
    
    class Meta:
        model = OnboardingData
        fields = ['city', 'team_size', 'contact', 'location']

