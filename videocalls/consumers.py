import json

from channels.generic.websocket import AsyncWebsocketConsumer

class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = self.scope['url_route']['kwargs']['room_name']

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data['type'] == 'offer':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type' : 'offer',
                    'data' : data,
                }
            )
        
        elif data['type'] == 'answer':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type' : 'answer',
                    'data' : data,
                }
            )

        if data['type'] == 'ICE_candidate':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type' : 'ICE_candidate',
                    'data' : data,
                }
            )

    async def offer(self, event):
        data = event['data']
        await self.send(text_data=json.dumps(
            {
                'type' : 'offer',
                'offer': data['offer'],
            }
        ))

    async def answer(self, event):
        data = event['data']
        await self.send(text_data=json.dumps(
            {
                'type'  : 'answer',
                'answer': data['answer'],
            }
        ))

    async def ICE_candidate(self, event):
        data = event['data']
        await self.send(text_data=json.dumps(
            {
                'type'         : 'ICE_candidate',
                'ice_candidate': data['ice_candidate'],
            }
        ))