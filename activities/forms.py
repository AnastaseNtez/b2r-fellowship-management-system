from django import forms
from .models import TrainingActivity

class ActivityReportForm(forms.ModelForm):
    """
    Form for Fellows to submit and update their training activity reports.
    Fields are synchronized with the TrainingActivity model.
    """
    class Meta:
        model = TrainingActivity
        # These fields MUST match the field names in your models.py 
        # and be available for rendering in submit_report.html
        fields = [
            'date',  
            'village_name', 
            'number_of_farmers_trained', 
            'training_topic', 
            'training_method', 
            'duration_hours',
            'challenges_notes', 
            'success_stories', 
            'photos'
        ]
        
        # Widgets allow us to add Bootstrap classes and specific HTML attributes
        widgets = {
            'date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
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
                attrs={'class': 'form-control'}
            ),
            'duration_hours': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.5'}
            ),
            'photos': forms.ClearableFileInput(
                attrs={'class': 'form-control'}
            ),
        }

    def clean_number_of_farmers_trained(self):
        """Custom validation to ensure number of farmers is not negative."""
        count = self.cleaned_data.get('number_of_farmers_trained')
        if count is not None and count < 0:
            raise forms.ValidationError("The number of farmers trained cannot be negative.")
        return count