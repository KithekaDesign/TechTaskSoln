from notifications.models import Notification


def create_notification(user, message, title="Notification", notif_type="GENERAL",
                        related_proposal_id=None, related_project_id=None, **kwargs):
    """
    Safe, reusable helper to create notifications.
    All fields have sensible defaults so callers never crash.
    """
    Notification.objects.create(
        user=user,
        notif_type=notif_type,
        title=title,
        message=message,
        related_proposal_id=related_proposal_id,
        related_project_id=related_project_id,
    )