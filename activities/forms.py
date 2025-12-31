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
        # Added 'sector' to match your updated model
        fields = [
            'date',
            'sector', 
            'village_name', 
            'number_of_farmers_trained', 
            'training_topic', 
            'training_method', 
            'duration_hours',
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
            'duration_hours': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.5', 'min': '0.1', 'max': '12'}
            ),
            'photos': forms.ClearableFileInput(
                attrs={'class': 'form-control'}
            ),
        }

    def clean_date(self):
        """Redundant check to ensure the date is not in the future."""
        date = self.cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise forms.ValidationError("You cannot log an activity for a future date.")
        return date

    def clean_number_of_farmers_trained(self):
        """Ensures at least one farmer is trained to maintain accurate sum metrics."""
        count = self.cleaned_data.get('number_of_farmers_trained')
        if count is not None and count < 1:
            raise forms.ValidationError("The number of farmers trained must be at least 1.")
        return count