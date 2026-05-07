from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class TimeLog(models.Model):
    freelancer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='time_logs'
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='time_logs'
    )
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.CharField(max_length=500)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.freelancer} — {self.hours}h on {self.date}"
