from django import forms
from .models import TrainingActivity

class ActivityReportForm(forms.ModelForm):
    class Meta:
        model = TrainingActivity
        fields = ['date', 'activity_type', 'description', 'hours_spent', 'location_details']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'location_details': forms.TextInput(attrs={'placeholder': 'e.g., Gakenke Farm Office'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply consistent Bootstrap styling
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})