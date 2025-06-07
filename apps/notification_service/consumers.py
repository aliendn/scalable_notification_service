from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from apps.users.models import CompanyUser


class NotificationConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        user = self.scope["user"]

        if user is None or isinstance(user, AnonymousUser) or not user.is_authenticated:
            await self.close()
        else:
            self.user = user
            await self.channel_layer.group_add("notifications_managers", self.channel_name)

            await self.accept()


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("notifications_managers", self.channel_name)

    async def receive_json(self, content, **kwargs):
        await self.send_json({
            "message": "This is a read-only WebSocket for receiving notifications."
        })

    async def send_notification(self, event):
        await self.send_json({
            "type": "notification",
            "id": event['content']["id"],
            "title": event['content']["title"],
            "description": event['content']["description"],
            "priority": event['content']["priority"],
            "timestamp": event['content']["timestamp"]
        })

    # @sync_to_async
    # def _is_user_manager(self, user):
    #     return user.company_memberships.filter(
    #         role=CompanyUser.RoleChoices.MANAGER.value
    #     ).exists()
