from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

User = settings.AUTH_USER_MODEL


class Proposal(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]

    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='proposals'
    )
    freelancer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='proposals_submitted'
    )
    cover_letter = models.TextField()
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_time = models.IntegerField(help_text="Delivery time in days")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.freelancer} → {self.project.title} ({self.status})"


# ── Signal: notify client when proposal is submitted ─────────────────────────
@receiver(post_save, sender=Proposal)
def notify_client_on_proposal(sender, instance, created, **kwargs):
    if created:
        from notifications.models import Notification
        Notification.objects.create(
            user=instance.project.client,
            notif_type='PROPOSAL',
            title='New Proposal Received',
            message=f'{instance.freelancer.username} submitted a proposal for "{instance.project.title}".',
            related_proposal_id=instance.id,
            related_project_id=instance.project.id,
        )