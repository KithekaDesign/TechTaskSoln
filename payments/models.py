from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Payment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RELEASED', 'Released'),
        ('DISPUTED', 'Disputed'),
    ]

    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    payer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments_made'
    )
    payee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments_received'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Payment #{self.pk} — {self.amount} ({self.status})"
