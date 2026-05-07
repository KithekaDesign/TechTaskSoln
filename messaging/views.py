from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from projects.models import Message
from .serializers import MessageSerializer


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter messages by project if ?project= query param is provided."""
        qs = Message.objects.all().order_by('timestamp')
        project_id = self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
