from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


# ======================
# PROJECT MODEL
# ======================

class Project(models.Model):

    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]

    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='client_projects'
    )

    title = models.CharField(max_length=255)

    description = models.TextField()

    budget = models.DecimalField(max_digits=10, decimal_places=2)

    required_skills = models.TextField()

    deadline = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='OPEN'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.title)


# ======================
# CHAT MESSAGE MODEL
# ======================

class Message(models.Model):

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    content = models.TextField()

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} - {self.project}"