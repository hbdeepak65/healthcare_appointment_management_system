from rest_framework import permissions


class IsPatient(permissions.BasePermission):
    """
    Custom permission to only allow patients to access certain views.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               hasattr(request.user, 'profile') and request.user.profile.role == 'PATIENT'


class IsDoctor(permissions.BasePermission):
    """
    Custom permission to only allow doctors to access certain views.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               hasattr(request.user, 'profile') and request.user.profile.role == 'DOCTOR'


class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admins to access certain views.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN'


class IsDoctorOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow doctors or admins to access certain views.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               hasattr(request.user, 'profile') and \
               request.user.profile.role in ['DOCTOR', 'ADMIN']


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN':
            return True
        
        # Check if the object belongs to the user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'patient'):
            return obj.patient == request.user
        
        return False