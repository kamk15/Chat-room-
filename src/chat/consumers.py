import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Store connection state
        self.connected = True

        try:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        except Exception as e:
            self.connected = False
            raise StopConsumer()

    async def disconnect(self, close_code):
        self.connected = False
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception:
            pass

    async def receive(self, text_data):
        if not self.connected:
            return

        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message
                }
            )
        except Exception:
            pass

    async def chat_message(self, event):
        if not self.connected:
            return

        try:
            message = event['message']
            await self.send(text_data=json.dumps({'message': message}))
        except Exception:
            self.connected = False

        


