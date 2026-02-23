from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, DoctorProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class DoctorProfileSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(read_only=True)
    doctor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DoctorProfile
        fields = '__all__'
        
    def get_doctor_name(self, obj):
        return obj.user_profile.user.get_full_name() or obj.user_profile.user.username


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, label='Confirm Password')
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES, default='PATIENT')
    phone = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'role', 'phone']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password2')
        role = validated_data.pop('role', 'PATIENT')
        phone = validated_data.pop('phone', '')

        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        # Update the automatically created profile
        profile = user.profile
        profile.role = role
        profile.phone = phone
        profile.save()

        return user


class DoctorRegistrationSerializer(serializers.Serializer):
    # User fields
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    
    # Doctor-specific fields
    specialization = serializers.ChoiceField(choices=DoctorProfile.SPECIALIZATION_CHOICES)
    license_number = serializers.CharField(required=True)
    years_of_experience = serializers.IntegerField(default=0)
    consultation_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bio = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        if DoctorProfile.objects.filter(license_number=attrs['license_number']).exists():
            raise serializers.ValidationError({"license_number": "A doctor with this license number already exists."})
        
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password2')
        phone = validated_data.pop('phone', '')
        
        # Doctor-specific fields
        specialization = validated_data.pop('specialization')
        license_number = validated_data.pop('license_number')
        years_of_experience = validated_data.pop('years_of_experience', 0)
        consultation_fee = validated_data.pop('consultation_fee', 0.00)
        bio = validated_data.pop('bio', '')

        # Create user
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        # Update profile to DOCTOR
        profile = user.profile
        profile.role = 'DOCTOR'
        profile.phone = phone
        profile.save()

        # Create doctor profile
        doctor_profile = DoctorProfile.objects.create(
            user_profile=profile,
            specialization=specialization,
            license_number=license_number,
            years_of_experience=years_of_experience,
            consultation_fee=consultation_fee,
            bio=bio
        )

        return user


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'date_of_birth', 'profile_picture']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        
        # Update user fields
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()
        
        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance