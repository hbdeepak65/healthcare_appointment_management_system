from django.contrib import admin
from .models import UserProfile, DoctorProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'role')
        }),
        ('Contact Details', {
            'fields': ('phone', 'address')
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'profile_picture')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['get_doctor_name', 'specialization', 'license_number', 'is_available', 'consultation_fee']
    list_filter = ['specialization', 'is_available']
    search_fields = ['user_profile__user__username', 'user_profile__user__email', 'license_number']
    
    fieldsets = (
        ('Doctor Information', {
            'fields': ('user_profile', 'specialization', 'license_number')
        }),
        ('Professional Details', {
            'fields': ('years_of_experience', 'consultation_fee', 'bio')
        }),
        ('Availability', {
            'fields': ('available_days', 'available_time_start', 'available_time_end', 'is_available')
        }),
    )
    
    def get_doctor_name(self, obj):
        return obj.user_profile.user.get_full_name() or obj.user_profile.user.username
    get_doctor_name.short_description = 'Doctor Name'