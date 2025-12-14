# fellows/views.py (The definitive corrected view)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string 

from .forms import FellowRegistrationForm
from accounts.models import UserProfile 
from .models import Fellow 

User = get_user_model()

def fellow_register_view(request):
    """
    Handles the registration of a new Fellow via a web form.
    It atomically creates a Django User, a UserProfile (Role: Fellow), and the Fellow record.
    """
    if request.method == 'POST':
        form = FellowRegistrationForm(request.POST)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # 1. Prepare Data for User/Fellow Creation
                    
                    # --- CRITICAL FIX: POP custom fields for User creation ---
                    email = form.cleaned_data.pop('email')
                    first_name = form.cleaned_data.pop('first_name') # <-- ADDED POP
                    last_name = form.cleaned_data.pop('last_name')   # <-- ADDED POP
                    
                    # Remove temporary location fields
                    form.cleaned_data.pop('province')
                    form.cleaned_data.pop('district')
                    
                    # 2. CREATE DJANGO USER ACCOUNT
                    raw_password = get_random_string(length=12) 
                    
                    user = User.objects.create_user(
                        username=email, 
                        email=email,
                        password=raw_password, 
                        # Use the variables we extracted above
                        first_name=first_name, 
                        last_name=last_name,
                        is_active=True
                    )

                    # 3. CREATE USER PROFILE (Assign Role)
                    UserProfile.objects.create(
                        user=user,
                        role=UserProfile.Role.FELLOW 
                    )
                    
                    # 4. CREATE FELLOW RECORD
                    # form.save() now only processes fields that belong to the Fellow model.
                    fellow = form.save(commit=False)
                    fellow.user = user 
                    fellow.save()
                    
                    messages.success(request, 
                        f"Fellow {fellow.get_full_name} registered successfully. " # Note: .get_full_name is a property, not a method
                        f"Temporary Password: {raw_password}"
                    )
                    
                    return redirect('/admin/') 

            except Exception as e:
                messages.error(request, 
                    f"Error during registration. Please check the provided data: {e}"
                )
                print(f"Error during registration: {e}") 
        
    else:
        form = FellowRegistrationForm()

    return render(request, 'fellows/fellow_form.html', {'form': form})