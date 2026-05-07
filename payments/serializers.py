from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    payer_username = serializers.CharField(source='payer.username', read_only=True)
    payee_username = serializers.CharField(source='payee.username', read_only=True)
    project_title = serializers.CharField(source='project.title', read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['payer']
