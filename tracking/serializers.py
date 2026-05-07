from rest_framework import serializers
from .models import TimeLog


class TimeLogSerializer(serializers.ModelSerializer):
    freelancer_username = serializers.CharField(source='freelancer.username', read_only=True)
    project_title = serializers.CharField(source='project.title', read_only=True)

    class Meta:
        model = TimeLog
        fields = '__all__'
        read_only_fields = ['freelancer']
