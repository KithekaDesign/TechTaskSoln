from django.contrib import admin
from .models import Project, Message
from proposals.models import Proposal
from notifications.models import Notification

admin.site.register(Project)
admin.site.register(Message)
admin.site.register(Proposal)
admin.site.register(Notification)