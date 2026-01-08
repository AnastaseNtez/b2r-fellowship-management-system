from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User # Added for API
from rest_framework import generics # Added for API
from rest_framework.permissions import AllowAny # Added for API

from .models import UserProfile
from .serializers import RegisterSerializer 

""" Script that handles where users go after they log in """

@login_required
def smart_redirect(request):
    role = request.user.userprofile.role
    if role == 'FELLOW':
        return redirect('fellow_dashboard')  
    elif role in ['ADMIN', 'COORDINATOR', 'MENTOR']:
        return redirect('mentor_dashboard')
    return redirect('login')

# ---API VIEW ---
class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Handles API-based registration for new users.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,) # Open to public
    serializer_class = RegisterSerializer