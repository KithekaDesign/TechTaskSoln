from rest_framework import serializers
from .models import User, FreelancerProfile, ClientProfile
from .utils import send_otp_email


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=['client', 'freelancer'], write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'role']

    def validate(self, attrs):  # type: ignore[override]
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        role = validated_data.pop('role')
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.is_client = (role == 'client')  # type: ignore[assignment]
        user.is_freelancer = (role == 'freelancer')  # type: ignore[assignment]
        user.is_active = False          # type: ignore[assignment]  # blocks login until email is verified
        user.is_email_verified = False  # type: ignore[assignment]
        user.save()

        # Send OTP
        otp = user.generate_otp()
        send_otp_email(user.email, otp)

        # Auto-create role profile
        if role == 'freelancer':
            FreelancerProfile.objects.create(  # type: ignore[attr-defined]
                user=user,
                skills='',
                experience_level='Entry',
                hourly_rate=0
            )
        else:
            ClientProfile.objects.create(user=user)  # type: ignore[attr-defined]

        return user


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


# --- Unchanged serializers below ---

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_client', 'is_freelancer', 'is_staff', 'is_superuser']


# UPDATE FreelancerProfileSerializer in accounts/serializers.py
# Replace the existing FreelancerProfileSerializer with this:

class FreelancerProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    bio = serializers.CharField(source='user.bio', read_only=True)
    profile_picture = serializers.ImageField(source='user.profile_picture', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    member_since = serializers.SerializerMethodField()

    class Meta:
        model = FreelancerProfile
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'bio', 'profile_picture', 'skills', 'experience_level',
            'category', 'hourly_rate', 'rating', 'completed_projects',
            'portfolio_link', 'title', 'location', 'languages',
            'availability', 'eth_wallet_address', 'total_earnings',
            'member_since',
        ]

    def get_member_since(self, obj):
        return obj.user.date_joined.strftime('%B %Y')


class UserAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_client', 'is_freelancer',
                  'is_active', 'is_staff', 'date_joined']
        


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'is_client', 'is_freelancer', 
                  'is_staff', 'is_email_verified', 'date_joined']
        read_only_fields = ['id', 'date_joined']