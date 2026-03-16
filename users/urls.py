from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginView, RegisterView, FamilyMemberViewSet

# Create a router for FamilyMember endpoints
router = DefaultRouter()
router.register(r'users', FamilyMemberViewSet, basename='family-member')

urlpatterns = [
    # Auth
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),

    # Family members API
    path('', include(router.urls)),
]