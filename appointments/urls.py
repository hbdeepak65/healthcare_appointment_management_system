from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AppointmentViewSet, MedicalRecordViewSet,
    TimeSlotViewSet, ReviewViewSet
)

router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'medical-records', MedicalRecordViewSet, basename='medical-record')
router.register(r'time-slots', TimeSlotViewSet, basename='time-slot')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]