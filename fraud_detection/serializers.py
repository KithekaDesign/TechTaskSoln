from rest_framework import serializers
from .models import FraudFlag


class FraudFlagSerializer(serializers.ModelSerializer):
    flagged_user_username = serializers.CharField(source='flagged_user.username', read_only=True)

    class Meta:
        model = FraudFlag
        fields = '__all__'
