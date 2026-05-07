from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
import random


class User(AbstractUser):
    email = models.EmailField(unique=True)

    is_client = models.BooleanField(default=False)
    is_freelancer = models.BooleanField(default=False)

    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)

    # Email verification fields
    is_email_verified = models.BooleanField(default=False)
    email_otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def generate_otp(self):
        self.email_otp = str(random.randint(100000, 999999))
        self.otp_created_at = timezone.now()
        self.save()
        return self.email_otp

    def __str__(self):
        return self.username


CATEGORY_CHOICES = [
    ('web_development', 'Web Development'),
    ('data_science', 'Data Science'),
    ('ai_ml', 'AI & ML'),
    ('cloud_infra', 'Cloud Infra'),
    ('app_development', 'App Development'),
    ('networking', 'Networking'),
    ('graphic_design', 'Graphic Design'),
    ('cybersecurity', 'Cybersecurity'),
]

AVAILABILITY_CHOICES = [
    ('available', 'Available'),
    ('busy', 'Busy'),
    ('not_available', 'Not Available'),
]


class FreelancerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    skills = models.TextField()
    experience_level = models.CharField(max_length=50)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='web_development'
    )
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField(default=0)
    completed_projects = models.IntegerField(default=0)
    portfolio_link = models.URLField(blank=True)

    title = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    languages = models.CharField(max_length=200, blank=True)
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='available')
    eth_wallet_address = models.CharField(max_length=42, blank=True, null=True)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} Freelancer Profile"


class ClientProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    company_name = models.CharField(max_length=255, blank=True)
    total_projects_posted = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} Client Profile"