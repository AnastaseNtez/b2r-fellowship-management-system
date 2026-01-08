from django import forms
from django.contrib.auth.models import User
from .models import Fellow

class FellowForm(forms.ModelForm):
    """
    Form to handle Fellow profile management.
    Includes additional fields to manage the linked User account.
    """
    first_name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'})
    )
    last_name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'})
    )

    class Meta:
        model = Fellow
        # Fields from the Fellow model
        fields = ['assigned_sector', 'status']
        widgets = {
            'assigned_sector': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        """Pre-populate User fields if editing an existing Fellow."""
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def clean_email(self):
        """Ensure the email is unique for new users."""
        email = self.cleaned_data.get('email')
        # Check if another user already uses this email (excluding the current user being edited)
        user_qs = User.objects.filter(email=email)
        if self.instance and self.instance.user:
            user_qs = user_qs.exclude(pk=self.instance.user.pk)
        
        if user_qs.exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        """
        Custom save method to sync the User and Fellow models.
        """
        email = self.cleaned_data['email']
        user_data = {
            'first_name': self.cleaned_data['first_name'],
            'last_name': self.cleaned_data['last_name'],
            'email': email,
            'username': email, # Set username to email for simplicity
        }

        if self.instance.pk:
            # UPDATE: Update the existing User object
            user = self.instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()
            fellow = super().save(commit=False)
        else:
            # CREATE: Create a new User and link to the new Fellow
            user = User.objects.create(**user_data)
            # might want to set a default password for new users
            user.set_password('B2RFarms2026!') 
            user.save()
            fellow = super().save(commit=False)
            fellow.user = user

        if commit:
            fellow.save()
        return fellow