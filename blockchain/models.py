from django.db import models
from django.conf import settings


class EscrowTransaction(models.Model):

    STATUS_CHOICES = [
        ('EMPTY', 'Empty'),
        ('FUNDED', 'Funded'),
        ('RELEASED', 'Released'),
        ('REFUNDED', 'Refunded'),
        ('DISPUTED', 'Disputed'),
    ]

    project = models.OneToOneField(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='escrow'
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='escrow_as_client'
    )
    freelancer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='escrow_as_freelancer'
    )
    client_wallet = models.CharField(max_length=42, blank=True, default='')
    freelancer_wallet = models.CharField(max_length=42, blank=True, default='')
    amount_eth = models.DecimalField(max_digits=18, decimal_places=8)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='EMPTY')
    tx_hash_funded = models.CharField(max_length=66, blank=True, null=True)
    tx_hash_released = models.CharField(max_length=66, blank=True, null=True)
    tx_hash_refunded = models.CharField(max_length=66, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Escrow for Project {self.project_id} — {self.status}"