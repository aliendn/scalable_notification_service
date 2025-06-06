from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]

        if user is None or isinstance(user, AnonymousUser) or not user.is_authenticated:
            await self.close()
        else:
            self.user = user
            self.group_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        # Optional: Echo or trigger something (usually handled server-side only)
        await self.send_json({
            "message": "This is a read-only WebSocket for receiving notifications."
        })

    async def send_notification(self, event):
        await self.send_json({
            "type": "notification",
            "title": event['content']["title"],
            "description": event['content']["description"],
            "priority": event['content']["priority"],
            "timestamp": event['content']["timestamp"]
        })
