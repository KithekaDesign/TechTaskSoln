from django.urls import path
from .views import (
    NotificationListView, NotificationUnreadCountView,
    MarkNotificationReadView, MarkAllReadView
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notifications'),
    path('unread-count/', NotificationUnreadCountView.as_view(), name='unread_count'),
    path('<int:pk>/read/', MarkNotificationReadView.as_view(), name='mark_read'),
    path('mark-all-read/', MarkAllReadView.as_view(), name='mark_all_read'),
]