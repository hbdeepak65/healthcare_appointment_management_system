from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({
        'message': 'Healthcare Appointment System API',
        'version': '1.0',
        'endpoints': {
            'admin': '/admin/',
            'auth': '/api/auth/',
            'users': '/api/users/',
            'appointments': '/api/appointments/',
        }
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/users/', include('users.urls')),
    path('api/appointments/', include('appointments.urls')),
]