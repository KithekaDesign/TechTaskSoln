from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework import serializers as drf_serializers
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone
from datetime import timedelta
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import User, FreelancerProfile, ClientProfile
from .serializers import (
    RegisterSerializer, UserInfoSerializer,
    FreelancerProfileSerializer, UserAdminSerializer,
    VerifyOTPSerializer, ResendOTPSerializer, UserSerializer
)
from .utils import send_otp_email


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # Tell SimpleJWT to use 'email' as the login credential field
    username_field = 'email'

    def validate(self, attrs):
        # ------------------------------------------------------------------
        # Email-based login:
        # Look up the user by email, verify password + account state, then
        # hand off to super() for token generation.
        # We temporarily set user.username = user.email so that Django's
        # authenticate() can find the user via the base serializer which
        # internally calls authenticate(username=..., password=...).
        # ------------------------------------------------------------------
        email = attrs.get('email', '').strip().lower()

        try:
            user_obj = User.objects.get(email__iexact=email)
        except User.DoesNotExist:  # type: ignore[attr-defined]
            raise drf_serializers.ValidationError(
                {'detail': 'No account found with that email address. Please check and try again.'}
            )

        # Check password before revealing account status (security best practice)
        if not user_obj.check_password(attrs.get('password', '')):
            raise drf_serializers.ValidationError(
                {'detail': 'Incorrect password. Please try again.'}
            )

        # Account exists with correct password — check email verification
        if not user_obj.is_email_verified:
            raise drf_serializers.ValidationError(
                {'detail': 'Please verify your email before logging in. '
                           'Check your inbox for the 6-digit verification code.'}
            )

        # Account deactivated by admin (after being verified)
        if not user_obj.is_active:
            raise drf_serializers.ValidationError(
                {'detail': 'Your account has been deactivated. Please contact support.'}
            )

        # Patch attrs so the parent serializer's authenticate() call works.
        # SimpleJWT passes username_field value to Django authenticate(),
        # but our AUTH_BACKEND looks up by email — so we pass email as 'username'.
        attrs[self.username_field] = user_obj.email

        # All checks pass — proceed with normal JWT token generation
        data = super().validate(attrs)
        return data


class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                'message': 'Account created. Check your email for a 6-digit verification code.',
                'username': user.username,
                'email': user.email,
            },
            status=status.HTTP_201_CREATED
        )


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:  # type: ignore[attr-defined]
            return Response(
                {'error': 'No account found with that email.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if user.is_email_verified:
            return Response(
                {'message': 'Email is already verified. Please log in.'},
                status=status.HTTP_200_OK
            )

        # Check OTP expiry (10 minutes)
        if not user.otp_created_at or \
           timezone.now() > user.otp_created_at + timedelta(minutes=10):
            return Response(
                {'error': 'OTP has expired. Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.email_otp != otp:
            return Response(
                {'error': 'Invalid code. Please try again.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Activate account
        user.is_email_verified = True
        user.is_active = True
        user.email_otp = None
        user.otp_created_at = None
        user.save()

        return Response(
            {'message': 'Email verified successfully. You can now log in.'},
            status=status.HTTP_200_OK
        )


class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email, is_email_verified=False)
        except User.DoesNotExist:  # type: ignore[attr-defined]
            return Response(
                {'error': 'No unverified account found with that email.'},
                status=status.HTTP_404_NOT_FOUND
            )

        otp = user.generate_otp()
        send_otp_email(user.email, otp)
        return Response(
            {'message': 'A new verification code has been sent to your email.'},
            status=status.HTTP_200_OK
        )


# --- Unchanged views below ---

class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserInfoSerializer(request.user)
        return Response(serializer.data)


from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

class LogoutView(APIView):
    """
    Accepts the refresh token in the request body and blacklists it,
    immediately invalidating the session even before the access token expires.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {'message': 'Logged out successfully.'},
                status=status.HTTP_205_RESET_CONTENT
            )
        except TokenError as e:
            return Response(
                {'error': 'Token is invalid or already blacklisted.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class FreelancerListView(generics.ListAPIView):
    serializer_class = FreelancerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = FreelancerProfile.objects.select_related('user').all()  # type: ignore[attr-defined]
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        return qs


class PublicFreelancerListView(generics.ListAPIView):
    serializer_class = FreelancerProfileSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = FreelancerProfile.objects.select_related('user').all()  # type: ignore[attr-defined]
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        return qs


from rest_framework.permissions import IsAuthenticated, IsAdminUser

class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = User.objects.all().order_by('-date_joined')

class FreelancerProfileDetailView(APIView):
    """
    GET  /api/auth/freelancers/<id>/profile/  — public profile view
    PUT  /api/auth/freelancers/me/profile/    — freelancer updates own profile
    """
    permission_classes = [AllowAny]
 
    def get(self, request, pk=None):
        try:
            profile = FreelancerProfile.objects.select_related('user').get(pk=pk)  # type: ignore[attr-defined]
        except FreelancerProfile.DoesNotExist:  # type: ignore[attr-defined]
            return Response({'error': 'Profile not found.'}, status=404)
 
        serializer = FreelancerProfileSerializer(profile, context={'request': request})
        data = serializer.data
 
        # Add user-level fields
        data['first_name'] = profile.user.first_name
        data['last_name'] = profile.user.last_name
        data['member_since'] = profile.user.date_joined.strftime('%B %Y')
 
        return Response(data)
 
 
class FreelancerProfileUpdateView(APIView):
    """
    PUT /api/auth/profile/update/ — freelancer updates their own profile
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
 
    def get(self, request):
        try:
            profile = FreelancerProfile.objects.get(user=request.user)  # type: ignore[attr-defined]
        except FreelancerProfile.DoesNotExist:  # type: ignore[attr-defined]
            return Response({'error': 'No freelancer profile found.'}, status=404)
        serializer = FreelancerProfileSerializer(profile, context={'request': request})
        data = serializer.data
        data['first_name'] = request.user.first_name
        data['last_name'] = request.user.last_name
        data['email'] = request.user.email
        return Response(data)
 
    def put(self, request):
        try:
            profile = FreelancerProfile.objects.get(user=request.user)  # type: ignore[attr-defined]
        except FreelancerProfile.DoesNotExist:  # type: ignore[attr-defined]
            return Response({'error': 'No freelancer profile found.'}, status=404)
 
        # Update user-level fields
        user = request.user
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        if 'bio' in request.data:
            user.bio = request.data['bio']
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        user.save()
 
        # Update profile-level fields
        allowed = [
            'skills', 'experience_level', 'category', 'hourly_rate',
            'portfolio_link', 'title', 'location', 'languages',
            'availability', 'eth_wallet_address'
        ]
        for field in allowed:
            if field in request.data:
                setattr(profile, field, request.data[field])
        profile.save()
 
        serializer = FreelancerProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)