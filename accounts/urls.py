from django.urls import path
from .views import (
    RegisterView, UserInfoView, LogoutView,
    FreelancerListView, PublicFreelancerListView, UserListView,
    VerifyOTPView, ResendOTPView, FreelancerProfileDetailView, FreelancerProfileUpdateView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyOTPView.as_view(), name='verify_email'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend_otp'),
    path('me/', UserInfoView.as_view(), name='user_info'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('freelancers/', FreelancerListView.as_view(), name='freelancer_list'),
    path('freelancers/public/', PublicFreelancerListView.as_view(), name='public_freelancer_list'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('freelancers/<int:pk>/profile/', FreelancerProfileDetailView.as_view(), name='freelancer_profile'),
    path('profile/update/', FreelancerProfileUpdateView.as_view(), name='profile_update'),
]