from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'notif_type', 'title', 'message',
            'is_read', 'related_proposal_id', 'related_project_id', 'created_at'
        ]


class NotificationListView(APIView):
    """
    GET /api/notifications/
    Returns all notifications for logged-in user, newest first.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
        serializer = NotificationSerializer(notifs, many=True)
        return Response({
            'notifications': serializer.data,
            'unread_count': notifs.filter(is_read=False).count(),
        })


class NotificationUnreadCountView(APIView):
    """
    GET /api/notifications/unread-count/
    Lightweight endpoint — used by navbar badge.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': count})


class MarkNotificationReadView(APIView):
    """
    POST /api/notifications/<id>/read/
    Mark a single notification as read.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            notif = Notification.objects.get(pk=pk, user=request.user)
            notif.is_read = True
            notif.save()
            return Response({'message': 'Marked as read.'})
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found.'}, status=404)


class MarkAllReadView(APIView):
    """
    POST /api/notifications/mark-all-read/
    Mark all notifications as read.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'message': 'All notifications marked as read.'})