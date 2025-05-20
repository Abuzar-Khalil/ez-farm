from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

# Create a router and register the UserViewSet under 'users'
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

# Include the router's URLs
urlpatterns = [
    path('', include(router.urls)),
]
