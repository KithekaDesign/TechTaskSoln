from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import TimeLog
from .serializers import TimeLogSerializer


class TimeLogViewSet(viewsets.ModelViewSet):
    queryset = TimeLog.objects.all()
    serializer_class = TimeLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return TimeLog.objects.all().order_by('-date')
        return TimeLog.objects.filter(freelancer=user).order_by('-date')

    def perform_create(self, serializer):
        serializer.save(freelancer=self.request.user)
