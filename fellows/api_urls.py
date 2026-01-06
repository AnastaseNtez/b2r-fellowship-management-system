# fellows/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FellowViewSet

router = DefaultRouter()
router.register(r'', FellowViewSet, basename='fellow-api')

urlpatterns = [
    path('', include(router.urls)),
]