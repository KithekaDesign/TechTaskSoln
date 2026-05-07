from rest_framework import serializers
from projects.models import Message


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    project_title = serializers.CharField(source='project.title', read_only=True)

    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['sender']
