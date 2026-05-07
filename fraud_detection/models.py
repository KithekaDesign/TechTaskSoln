from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class FraudFlag(models.Model):
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    flagged_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='fraud_flags'
    )
    reason = models.TextField()
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default='MEDIUM'
    )
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Fraud Flag — {self.flagged_user} ({self.severity})"
