from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def send_notification(recipient, notif_type, message, reference_id=None):
    """Create a notification and push it via WebSocket."""
    from .models import Notification
    notif = Notification.objects.create(
        recipient=recipient,
        notif_type=notif_type,
        message=message,
        reference_id=reference_id,
    )
    # Push via WebSocket
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notifications_{recipient.id}',
            {
                'type': 'send_notification',
                'id': notif.id,
                'notif_type': notif_type,
                'message': message,
                'reference_id': reference_id,
                'created_at': notif.created_at.isoformat(),
            }
        )
    except Exception:
        pass  # WebSocket push is best-effort
    return notif
