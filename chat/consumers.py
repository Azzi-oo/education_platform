import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.id = self.scope['url_route']['kwargs']['course_id']
        self.room_group_name = f'chat_{self.id}'
        # присоединиться к группе чат-комнаты
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        # принять соединение
        self.accept()

    def disconnect(self, close_code):
        # покинуть группу чат-комнаты
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # получить сообщения из WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # отправить сообщение в группу чат-комнаты
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
            }
        )
        # отправить сообщение в Вебсокет
        self.send(text_data=json.dumps({'message': message}))

    def chat_message(self, event):
        # отправить сообщение в веб-сокет
        self.send(text_data=json.dumps(event))
