from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    TYPE_CHOICES = [
        ('PROPOSAL',   'New Proposal'),
        ('ACCEPTED',   'Proposal Accepted'),
        ('REJECTED',   'Proposal Rejected'),
        ('FUNDED',     'Escrow Funded'),
        ('RELEASED',   'Payment Released'),
        ('COMPLETED',  'Project Completed'),
        ('DISPUTED',   'Dispute Raised'),
        ('MESSAGE',    'New Message'),
        ('GENERAL',    'General'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notif_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='GENERAL')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    # Optional links back to related objects
    related_proposal_id = models.IntegerField(null=True, blank=True)
    related_project_id = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notif_type}] {self.title} → {self.user.username}"