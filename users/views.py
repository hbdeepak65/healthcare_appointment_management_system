from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from .models import UserProfile, DoctorProfile
from .serializers import (
    UserSerializer, UserProfileSerializer, DoctorProfileSerializer,
    UserRegistrationSerializer, DoctorRegistrationSerializer,
    UserProfileUpdateSerializer
)
from .permissions import IsDoctor, IsAdmin, IsDoctorOrAdmin


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration (patients)
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.profile.role,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class DoctorRegistrationView(generics.CreateAPIView):
    """
    API endpoint for doctor registration (requires admin approval in production)
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]  # Change to [IsAdmin] in production
    serializer_class = DoctorRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.profile.role,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Doctor registered successfully'
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    API endpoint for user login
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({
            'error': 'Please provide both username and password'
        }, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if not user:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)

    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.profile.role if hasattr(user, 'profile') else None,
        },
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    API endpoint for user logout (blacklist refresh token)
    """
    try:
        refresh_token = request.data.get('refresh_token')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Invalid token'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """
    Get current authenticated user details
    """
    user = request.user
    profile_serializer = UserProfileSerializer(user.profile)
    
    return Response({
        'user': profile_serializer.data
    }, status=status.HTTP_200_OK)


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user profile operations
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter queryset based on user role
        """
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.role == 'ADMIN':
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=user)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user's profile
        """
        serializer = self.get_serializer(request.user.profile)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """
        Update current user's profile
        """
        serializer = UserProfileUpdateSerializer(
            request.user.profile,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Profile updated successfully',
            'profile': UserProfileSerializer(request.user.profile).data
        })


class DoctorProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for doctor profile operations
    """
    queryset = DoctorProfile.objects.select_related('user_profile__user').all()
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter available doctors
        """
        queryset = DoctorProfile.objects.select_related('user_profile__user').filter(is_available=True)
        
        # Filter by specialization if provided
        specialization = self.request.query_params.get('specialization', None)
        if specialization:
            queryset = queryset.filter(specialization=specialization)
        
        return queryset

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """
        Get doctor's availability schedule
        """
        doctor = self.get_object()
        return Response({
            'doctor_id': doctor.id,
            'doctor_name': doctor.user_profile.user.get_full_name(),
            'available_days': doctor.available_days,
            'available_time_start': doctor.available_time_start,
            'available_time_end': doctor.available_time_end,
            'is_available': doctor.is_available,
        })