from rest_framework import serializers
from .models import Proposal
from accounts.serializers import FreelancerProfileSerializer
from accounts.models import FreelancerProfile


class ProposalSerializer(serializers.ModelSerializer):
    freelancer_username = serializers.CharField(source='freelancer.username', read_only=True)
    project_title = serializers.CharField(source='project.title', read_only=True)
    project_budget = serializers.DecimalField(source='project.budget', max_digits=10, decimal_places=2, read_only=True)
    freelancer_profile = serializers.SerializerMethodField()

    class Meta:
        model = Proposal
        fields = [
            'id', 'project', 'project_title', 'project_budget',
            'freelancer', 'freelancer_username', 'freelancer_profile',
            'cover_letter', 'bid_amount', 'delivery_time',
            'status', 'created_at',
        ]
        read_only_fields = ['freelancer', 'status', 'created_at']

    def get_freelancer_profile(self, obj):
        try:
            profile = FreelancerProfile.objects.get(user=obj.freelancer)
            return FreelancerProfileSerializer(profile).data
        except FreelancerProfile.DoesNotExist:
            return None