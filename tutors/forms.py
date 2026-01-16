from django import forms
from .models import TutorProfile, PricingOption, TutorDocument, Subject


class PricingOptionForm(forms.ModelForm):
    """Form for creating/editing pricing options"""
    class Meta:
        model = PricingOption
        fields = ['subject', 'mode', 'level', 'price_per_hour', 'is_active']
        widgets = {
            'subject': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}),
            'mode': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}),
            'level': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}),
            'price_per_hour': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm',
                'step': '0.01',
                'min': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300'}),
        }


class TutorDocumentForm(forms.ModelForm):
    """Form for uploading tutor documents"""
    class Meta:
        model = TutorDocument
        fields = ['document_type', 'document_file']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm'}),
            'document_file': forms.FileInput(attrs={'class': 'mt-1 block w-full text-sm text-gray-500'}),
        }

