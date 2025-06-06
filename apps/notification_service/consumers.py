import json

from channels.generic.websocket import WebsocketConsumer


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({"message": message}))

# from channels.generic.websocket import AsyncJsonWebsocketConsumer
# from channels.db import database_sync_to_async
# from .models import Notification
# from .serializers import NotificationSerializer
#
# class NotificationConsumer(AsyncJsonWebsocketConsumer):
#     async def connect(self):
#         user = self.scope["user"]
#         if user.is_authenticated:
#             await self.channel_layer.group_add(f"user_{user.id}", self.channel_name)
#             await self.accept()
#
#     async def disconnect(self, code):
#         user = self.scope["user"]
#         await self.channel_layer.group_discard(f"user_{user.id}", self.channel_name)
#
#     async def notify(self, event):
#         await self.send_json(event["content"])
