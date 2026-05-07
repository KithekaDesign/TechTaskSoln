from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    reported_by_username = serializers.CharField(source='reported_by.username', read_only=True)
    reported_user_username = serializers.CharField(source='reported_user.username', read_only=True)

    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ['reported_by']
