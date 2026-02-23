from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from users.models import DoctorProfile


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='doctor_appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True, help_text='Doctor\'s notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        unique_together = ['doctor', 'appointment_date', 'appointment_time']
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'

    def __str__(self):
        return f"{self.patient.username} - Dr. {self.doctor.user_profile.user.last_name} - {self.appointment_date} {self.appointment_time}"

    def clean(self):
        """
        Validate appointment data
        """
        # Check if appointment is in the past
        if self.appointment_date and self.appointment_time:
            appointment_datetime = timezone.make_aware(
                timezone.datetime.combine(self.appointment_date, self.appointment_time)
            )
            if appointment_datetime < timezone.now():
                raise ValidationError("Cannot book appointments in the past")

        # Check if doctor is available
        if self.doctor and not self.doctor.is_available:
            raise ValidationError("This doctor is not currently available")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class MedicalRecord(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medical_records')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='medical_record')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='created_records')
    diagnosis = models.TextField()
    prescription = models.TextField(blank=True, null=True)
    lab_results = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    attachments = models.JSONField(default=list, blank=True)  # Store URLs to file attachments
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Medical Record'
        verbose_name_plural = 'Medical Records'

    def __str__(self):
        return f"{self.patient.username} - {self.created_at.strftime('%Y-%m-%d')}"


class TimeSlot(models.Model):
    """
    Represents available time slots for doctors
    """
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='time_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ['doctor', 'date', 'start_time']
        verbose_name = 'Time Slot'
        verbose_name_plural = 'Time Slots'

    def __str__(self):
        return f"Dr. {self.doctor.user_profile.user.last_name} - {self.date} {self.start_time}-{self.end_time}"

    def clean(self):
        """
        Validate time slot data
        """
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")

        # Check if slot is in the past
        if self.date:
            slot_datetime = timezone.make_aware(
                timezone.datetime.combine(self.date, self.start_time)
            )
            if slot_datetime < timezone.now():
                raise ValidationError("Cannot create time slots in the past")


class Review(models.Model):
    """
    Patient reviews for doctors
    """
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='reviews')
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='review')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'

    def __str__(self):
        return f"{self.patient.username} - Dr. {self.doctor.user_profile.user.last_name} - {self.rating}★"

    def clean(self):
        """
        Validate review data
        """
        # Only allow reviews for completed appointments
        if self.appointment and self.appointment.status != 'COMPLETED':
            raise ValidationError("Can only review completed appointments")