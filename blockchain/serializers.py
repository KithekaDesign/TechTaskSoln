from rest_framework import serializers
from .models import EscrowTransaction


class EscrowTransactionSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source='project.title', read_only=True)
    client_username = serializers.CharField(source='client.username', read_only=True)
    freelancer_username = serializers.CharField(source='freelancer.username', read_only=True)

    class Meta:
        model = EscrowTransaction
        fields = [
            'id', 'project', 'project_title',
            'client', 'client_username',
            'freelancer', 'freelancer_username',
            'client_wallet', 'freelancer_wallet',
            'amount_eth', 'status',
            'tx_hash_funded', 'tx_hash_released', 'tx_hash_refunded',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'tx_hash_funded',
            'tx_hash_released', 'tx_hash_refunded',
            'created_at', 'updated_at',
        ]