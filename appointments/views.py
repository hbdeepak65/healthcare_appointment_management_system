from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Avg
from django.utils import timezone

from .models import Appointment, MedicalRecord, TimeSlot, Review
from .serializers import (
    AppointmentSerializer, AppointmentCreateSerializer,
    MedicalRecordSerializer, TimeSlotSerializer,
    ReviewSerializer, AppointmentStatsSerializer
)
from users.permissions import IsDoctor, IsPatient, IsDoctorOrAdmin


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing appointments
    """
    queryset = Appointment.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return AppointmentCreateSerializer
        return AppointmentSerializer

    def get_queryset(self):
        """
        Filter appointments based on user role
        """
        user = self.request.user
        queryset = Appointment.objects.select_related('patient', 'doctor__user_profile__user')

        if hasattr(user, 'profile'):
            if user.profile.role == 'PATIENT':
                queryset = queryset.filter(patient=user)
            elif user.profile.role == 'DOCTOR':
                queryset = queryset.filter(doctor__user_profile__user=user)
            # ADMIN sees all appointments

        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(appointment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(appointment_date__lte=end_date)

        return queryset

    def perform_create(self, serializer):
        """
        Set the patient to the current user when creating appointment
        """
        serializer.save(patient=self.request.user)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Confirm a pending appointment (Doctor/Admin only)
        """
        appointment = self.get_object()
        
        if appointment.status != 'PENDING':
            return Response({
                'error': 'Only pending appointments can be confirmed'
            }, status=status.HTTP_400_BAD_REQUEST)

        appointment.status = 'CONFIRMED'
        appointment.save()

        return Response({
            'message': 'Appointment confirmed successfully',
            'appointment': AppointmentSerializer(appointment).data
        })

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Mark appointment as completed (Doctor/Admin only)
        """
        appointment = self.get_object()
        
        if appointment.status not in ['PENDING', 'CONFIRMED']:
            return Response({
                'error': 'Only pending or confirmed appointments can be completed'
            }, status=status.HTTP_400_BAD_REQUEST)

        appointment.status = 'COMPLETED'
        appointment.notes = request.data.get('notes', appointment.notes)
        appointment.save()

        return Response({
            'message': 'Appointment completed successfully',
            'appointment': AppointmentSerializer(appointment).data
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel an appointment
        """
        appointment = self.get_object()
        
        if appointment.status in ['COMPLETED', 'CANCELLED']:
            return Response({
                'error': 'Cannot cancel completed or already cancelled appointments'
            }, status=status.HTTP_400_BAD_REQUEST)

        appointment.status = 'CANCELLED'
        appointment.save()

        return Response({
            'message': 'Appointment cancelled successfully',
            'appointment': AppointmentSerializer(appointment).data
        })

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        Get upcoming appointments for the current user
        """
        user = request.user
        today = timezone.now().date()
        
        if hasattr(user, 'profile') and user.profile.role == 'PATIENT':
            appointments = Appointment.objects.filter(
                patient=user,
                appointment_date__gte=today,
                status__in=['PENDING', 'CONFIRMED']
            ).order_by('appointment_date', 'appointment_time')
        elif hasattr(user, 'profile') and user.profile.role == 'DOCTOR':
            appointments = Appointment.objects.filter(
                doctor__user_profile__user=user,
                appointment_date__gte=today,
                status__in=['PENDING', 'CONFIRMED']
            ).order_by('appointment_date', 'appointment_time')
        else:
            appointments = Appointment.objects.filter(
                appointment_date__gte=today,
                status__in=['PENDING', 'CONFIRMED']
            ).order_by('appointment_date', 'appointment_time')

        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get appointment statistics
        """
        user = request.user
        
        if hasattr(user, 'profile') and user.profile.role == 'PATIENT':
            queryset = Appointment.objects.filter(patient=user)
        elif hasattr(user, 'profile') and user.profile.role == 'DOCTOR':
            queryset = Appointment.objects.filter(doctor__user_profile__user=user)
        else:
            queryset = Appointment.objects.all()

        stats = {
            'total_appointments': queryset.count(),
            'pending_appointments': queryset.filter(status='PENDING').count(),
            'confirmed_appointments': queryset.filter(status='CONFIRMED').count(),
            'completed_appointments': queryset.filter(status='COMPLETED').count(),
            'cancelled_appointments': queryset.filter(status='CANCELLED').count(),
        }

        serializer = AppointmentStatsSerializer(stats)
        return Response(serializer.data)


class MedicalRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing medical records
    """
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter medical records based on user role
        """
        user = self.request.user
        queryset = MedicalRecord.objects.select_related('patient', 'doctor__user_profile__user')

        if hasattr(user, 'profile'):
            if user.profile.role == 'PATIENT':
                queryset = queryset.filter(patient=user)
            elif user.profile.role == 'DOCTOR':
                queryset = queryset.filter(Q(doctor__user_profile__user=user) | Q(patient=user))
            # ADMIN sees all records

        return queryset

    def perform_create(self, serializer):
        """
        Set the doctor to the current user's doctor profile when creating record
        """
        if hasattr(self.request.user, 'profile') and hasattr(self.request.user.profile, 'doctor_profile'):
            serializer.save(doctor=self.request.user.profile.doctor_profile)
        else:
            raise ValidationError("Only doctors can create medical records")


class TimeSlotViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing time slots
    """
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter available time slots
        """
        queryset = TimeSlot.objects.select_related('doctor__user_profile__user')
        
        # Filter by doctor
        doctor_id = self.request.query_params.get('doctor', None)
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        
        # Filter by date
        date = self.request.query_params.get('date', None)
        if date:
            queryset = queryset.filter(date=date)
        
        # Filter by availability
        available_only = self.request.query_params.get('available_only', 'true')
        if available_only.lower() == 'true':
            queryset = queryset.filter(is_booked=False, date__gte=timezone.now().date())
        
        return queryset.order_by('date', 'start_time')

    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Get all available (unbooked) time slots
        """
        today = timezone.now().date()
        slots = TimeSlot.objects.filter(
            is_booked=False,
            date__gte=today
        ).order_by('date', 'start_time')
        
        serializer = self.get_serializer(slots, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reviews
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter reviews
        """
        queryset = Review.objects.select_related('patient', 'doctor__user_profile__user', 'appointment')
        
        # Filter by doctor
        doctor_id = self.request.query_params.get('doctor', None)
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        
        # Filter by patient (only show own reviews to patients)
        if hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'PATIENT':
            queryset = queryset.filter(patient=self.request.user)
        
        return queryset

    @action(detail=False, methods=['get'], url_path='doctor/(?P<doctor_id>[^/.]+)/stats')
    def doctor_stats(self, request, doctor_id=None):
        """
        Get review statistics for a specific doctor
        """
        reviews = Review.objects.filter(doctor_id=doctor_id)
        
        stats = {
            'total_reviews': reviews.count(),
            'average_rating': reviews.aggregate(Avg('rating'))['rating__avg'] or 0,
            'rating_distribution': {
                '5_star': reviews.filter(rating=5).count(),
                '4_star': reviews.filter(rating=4).count(),
                '3_star': reviews.filter(rating=3).count(),
                '2_star': reviews.filter(rating=2).count(),
                '1_star': reviews.filter(rating=1).count(),
            }
        }
        
        return Response(stats)