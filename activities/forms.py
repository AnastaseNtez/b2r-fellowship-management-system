from django import forms
from .models import TrainingActivity
from django.utils import timezone

class ActivityReportForm(forms.ModelForm):
    """
    Form for Fellows to submit and update their training activity reports.
    Validated against model constraints to ensure data integrity.
    """
    class Meta:
        model = TrainingActivity
        fields = [
            'date',
            'sector', 
            'village_name', 
            'number_of_farmers_trained', 
            'training_topic', 
            'training_method', 
            'duration',
            'challenges_notes', 
            'success_stories', 
            'photos'
        ]
        
        widgets = {
            'date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'sector': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'training_method': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'challenges_notes': forms.Textarea(
                attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'What obstacles did you face?'}
            ),
            'success_stories': forms.Textarea(
                attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Share any positive impact or feedback...'}
            ),
            'training_topic': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'e.g., Soil Conservation'}
            ),
            'village_name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'number_of_farmers_trained': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '1'}
            ),
            # Using TextInput to allow HH:MM:SS format 
            # This prevents the browser "valid values" error for decimals.
            'duration': forms.TextInput(
                attrs={
                    'class': 'form-control', 
                    'placeholder': 'HH:MM:SS (e.g., 02:30:00)',
                    'title': 'Enter duration as Hours:Minutes:Seconds'
                }
            ),
            'photos': forms.ClearableFileInput(
                attrs={'class': 'form-control'}
            ),
        }

    def clean_date(self):
        """Ensures the training date is not set in the future."""
        date = self.cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise forms.ValidationError("You cannot log an activity for a future date.")
        return date

    def clean_number_of_farmers_trained(self):
        """Ensures at least one farmer is recorded for impact metrics."""
        count = self.cleaned_data.get('number_of_farmers_trained')
        if count is not None and count < 1:
            raise forms.ValidationError("The number of farmers trained must be at least 1.")
        return count