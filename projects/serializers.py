from rest_framework import serializers
from projects.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    client_username = serializers.CharField(source='client.username', read_only=True)

    class Meta:
        model = Project
        fields = fields = ['id', 'title', 'description', 'budget', 'required_skills', 'deadline', 'status', 'client', 'client_username', 'created_at']
        read_only_fields = ['client']