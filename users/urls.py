from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserRegistrationView, DoctorRegistrationView,
    login_view, logout_view, current_user_view,
    UserProfileViewSet, DoctorProfileViewSet
)

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='userprofile')
router.register(r'doctors', DoctorProfileViewSet, basename='doctor')

urlpatterns = [
    # Authentication
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('register/doctor/', DoctorRegistrationView.as_view(), name='register-doctor'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('me/', current_user_view, name='current-user'),
    
    # Router URLs
    path('', include(router.urls)),
]