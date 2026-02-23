from django.contrib import admin
from .models import Appointment, MedicalRecord, TimeSlot, Review


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'get_doctor_name', 'appointment_date', 'appointment_time', 'status', 'created_at']
    list_filter = ['status', 'appointment_date', 'created_at']
    search_fields = ['patient__username', 'patient__email', 'doctor__user_profile__user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Appointment Details', {
            'fields': ('patient', 'doctor', 'appointment_date', 'appointment_time', 'status')
        }),
        ('Additional Information', {
            'fields': ('reason', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user_profile.user.get_full_name()}"
    get_doctor_name.short_description = 'Doctor'


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'get_doctor_name', 'appointment', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['patient__username', 'doctor__user_profile__user__username', 'diagnosis']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient', 'appointment', 'doctor')
        }),
        ('Medical Details', {
            'fields': ('diagnosis', 'prescription', 'lab_results', 'notes')
        }),
        ('Attachments', {
            'fields': ('attachments',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user_profile.user.get_full_name()}"
    get_doctor_name.short_description = 'Doctor'


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['get_doctor_name', 'date', 'start_time', 'end_time', 'is_booked']
    list_filter = ['is_booked', 'date']
    search_fields = ['doctor__user_profile__user__username']
    
    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user_profile.user.get_full_name()}"
    get_doctor_name.short_description = 'Doctor'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['patient', 'get_doctor_name', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['patient__username', 'doctor__user_profile__user__username', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user_profile.user.get_full_name()}"
    get_doctor_name.short_description = 'Doctor'