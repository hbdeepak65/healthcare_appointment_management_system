from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Appointment, MedicalRecord, TimeSlot, Review
from users.serializers import UserSerializer, DoctorProfileSerializer


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    doctor_details = DoctorProfileSerializer(source='doctor', read_only=True)
    
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_patient_name(self, obj):
        return obj.patient.get_full_name() or obj.patient.username

    def get_doctor_name(self, obj):
        return obj.doctor.user_profile.user.get_full_name() or obj.doctor.user_profile.user.username

    def validate(self, data):
        """
        Check that appointment is not in the past and doctor is available
        """
        from django.utils import timezone
        
        appointment_datetime = timezone.make_aware(
            timezone.datetime.combine(data['appointment_date'], data['appointment_time'])
        )
        
        if appointment_datetime < timezone.now():
            raise serializers.ValidationError("Cannot book appointments in the past")
        
        if not data['doctor'].is_available:
            raise serializers.ValidationError("This doctor is not currently available")
        
        # Check if slot is already booked
        existing = Appointment.objects.filter(
            doctor=data['doctor'],
            appointment_date=data['appointment_date'],
            appointment_time=data['appointment_time'],
            status__in=['PENDING', 'CONFIRMED']
        )
        
        if self.instance:
            existing = existing.exclude(id=self.instance.id)
        
        if existing.exists():
            raise serializers.ValidationError("This time slot is already booked")
        
        return data


class AppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time', 'reason']

    def create(self, validated_data):
        # Set patient from request user
        validated_data['patient'] = self.context['request'].user
        return super().create(validated_data)


class MedicalRecordSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = MedicalRecord
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_patient_name(self, obj):
        return obj.patient.get_full_name() or obj.patient.username

    def get_doctor_name(self, obj):
        return obj.doctor.user_profile.user.get_full_name() or obj.doctor.user_profile.user.username


class TimeSlotSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TimeSlot
        fields = '__all__'
        read_only_fields = ['id', 'is_booked', 'created_at']

    def get_doctor_name(self, obj):
        return obj.doctor.user_profile.user.get_full_name() or obj.doctor.user_profile.user.username

    def validate(self, data):
        """
        Validate time slot
        """
        from django.utils import timezone
        
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("End time must be after start time")
        
        slot_datetime = timezone.make_aware(
            timezone.datetime.combine(data['date'], data['start_time'])
        )
        
        if slot_datetime < timezone.now():
            raise serializers.ValidationError("Cannot create time slots in the past")
        
        return data


class ReviewSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['id', 'patient', 'created_at', 'updated_at']

    def get_patient_name(self, obj):
        return obj.patient.get_full_name() or obj.patient.username

    def get_doctor_name(self, obj):
        return obj.doctor.user_profile.user.get_full_name() or obj.doctor.user_profile.user.username

    def validate(self, data):
        """
        Validate review
        """
        appointment = data.get('appointment')
        
        if appointment and appointment.status != 'COMPLETED':
            raise serializers.ValidationError("Can only review completed appointments")
        
        if appointment and appointment.patient != self.context['request'].user:
            raise serializers.ValidationError("You can only review your own appointments")
        
        return data

    def create(self, validated_data):
        # Set patient from request user
        validated_data['patient'] = self.context['request'].user
        return super().create(validated_data)


class AppointmentStatsSerializer(serializers.Serializer):
    total_appointments = serializers.IntegerField()
    pending_appointments = serializers.IntegerField()
    confirmed_appointments = serializers.IntegerField()
    completed_appointments = serializers.IntegerField()
    cancelled_appointments = serializers.IntegerField()