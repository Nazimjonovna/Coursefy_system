from datetime import datetime
from ast import operator
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from json.decoder import JSONDecodeError

from django.dispatch import receiver
from django.contrib.auth import get_user_model
from chat.extra_func import create_msg, get_messages_by_chat, get_chats_by_user, get_chat_users, get_all_users, mark_as_read_chat_messages
from chat.models import Message
import json

from chat.serializers import MessageSerializer, UserSerializer
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync, sync_to_async
User = get_user_model()

channel_layer = get_channel_layer()


@database_sync_to_async
def update_key_query(object):
    object.save()


@database_sync_to_async
def get_key_query(model, key):
    return model.objects.get(id=key)


@database_sync_to_async
def delete_key_query(model, key):
    return model.objects.get(id=key).delete()


@database_sync_to_async
def filterMessages(model, kwargs):
    messages = model.objects.filter(**kwargs).order_by('id')

    serializer = MessageSerializer(
        messages, many=True, context={"receiver": receiver})
    return serializer.data


async def update_messages(sender, receiver, chat_id):
    messages = await get_messages_by_chat(sender, receiver, chat_id)

    await channel_layer.group_send(
        f"chat_of_{chat_id[0]}{chat_id[1]}_{sender}",
        {
            "type": "send.sender",
            "text": messages,
        }
    )

    messages = await get_messages_by_chat(receiver, sender, chat_id)

    await channel_layer.group_send(
        f"chat_of_{chat_id[0]}{chat_id[1]}_{receiver}",
        {
            "type": "send.receiver",
            "text": messages,
        }
    )


class UserOnlineStatus(AsyncJsonWebsocketConsumer):
    async def connect(self):
        pk = self.scope["url_route"]["kwargs"]["pk"]

        user = self.scope.get('user', False)

        await self.accept()

        if user.is_anonymous:
            await self.send_json({"user": str(user), 'errors': user.get_errors})
            return await self.close()

        self.room_group_name = f"user_online_{pk}"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        receiver = await get_key_query(User, pk)

        if receiver.last_online is not None:
            if datetime.today().date() > receiver.last_online.date():
                last_online = datetime.strftime(
                    receiver.last_online, '%Y-%m-%d')
            else:
                last_online = datetime.strftime(receiver.last_online, '%H:%M')
        else:
            last_online = None

        message = {
            "is_online": receiver.is_online,
            "last_online": last_online
        }

        return await self.send(
            json.dumps(
                message
            )
        )

    async def send_data(self, event):

        data = event['data']
        return await self.send_json(data)


class ChatListConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):

        user = self.scope.get('user', False)

        await self.accept()

        if user.is_anonymous:
            await self.send_json({"user": str(user), 'errors': user.get_errors})
            return await self.close()

        self.room_group_name = f"list_{user.id}"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        return await self.send(
            json.dumps(
                {
                    "message": "User connected",
                    # "user": str(user.id),
                    "user": user.id
                }
            )
        )

    async def receive(self, text_data):
        """
        ACTIONS : 'select-chat', 'create-message', 'mark-as-read-chat', 'mark-as-read-message';
        EXTRA ACTIONS : 'new-message', 'new-chat'
        """
        try:
            content = json.loads(text_data)
            if not isinstance(content, dict):
                return await self.send(
                    json.dumps(
                        {
                            'error': 'expected type json, got str instead'
                        }
                    )
                )
        except JSONDecodeError as e:
            return await self.send(json.dumps({'error': str(e)}))

        user = self.scope.get('user', False)
        user_inform = {"user": user.id}
        ACTIONS = ['select-chat', 'create-message', 'get-all-users']
        action = content.pop('action', False)

        await self.channel_layer.group_add(
            f"chatlist_{user.id}",
            self.channel_name
        )

        if not action:
            return await self.send_json({"errors": {"action": 'This field is required!'}})

        if action not in ACTIONS:
            return await self.send_json({'errors': {"action": f"enter one of the following : {ACTIONS}"}})

        if action == "get-all-users":

            users = await get_all_users(user.id)
            return await self.send(json.dumps({'users': users}))

    async def disconnect(self, code):
        user = self.scope.get('user', False)
        try:
            if not user.is_anonymous:

                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
        except Exception as e:
            print(e, "\n\n\n")
        finally:
            return await super().disconnect(code)

    async def send_data(self, event):

        data = event['data']
        return await self.send_json(data)


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):

        user = self.scope.get('user', False)

        await self.accept()

        if user.is_anonymous:
            await self.send_json({"user": str(user), 'errors': user.get_errors})
            return await self.close()

        self.room_group_name = f"{user.id}"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        return await self.send(
            json.dumps(
                {
                    "message": "User connected",
                    # "user": str(user.id),
                    "user": await get_chat_users(user)
                }
            )
        )

    async def receive(self, text_data):
        """
        ACTIONS : 'select-chat', 'create-message', 'mark-as-read-chat', 'mark-as-read-message';
        EXTRA ACTIONS : 'new-message', 'new-chat'
        """
        try:
            content = json.loads(text_data)
            if not isinstance(content, dict):
                return await self.send(
                    json.dumps(
                        {
                            'error': 'expected type json, got str instead'
                        }
                    )
                )
        except JSONDecodeError as e:
            return await self.send(json.dumps({'error': str(e)}))

        user = self.scope.get('user', False)

        ACTIONS = ['select-chat', 'send-message',
                   'get-all-users', 'edit', 'delete', 'mark-as-read']
        action = content.pop('action', False)

        if not action:
            return await self.send_json({"errors": {"action": 'This field is required!'}})

        if action not in ACTIONS:
            return await self.send_json({'errors': {"action": f"enter one of the following : {ACTIONS}"}})

        if action == 'select-chat':

            receiver = content.pop('receiver', False)
            sender = self.scope.get('user', False)
            chat_id = sorted([receiver, sender.id])

            self.room_group_name = f"chat_of_{chat_id[0]}{chat_id[1]}_{sender.id}"

            user.is_online = True
            await update_key_query(user)

            message = {
                "is_online": sender.is_online,
                "last_online": ""
            }

            await self.channel_layer.group_send(
                f"user_online_{sender.id}",
                {
                    "type": "send.data",
                    "data": message,
                }
            )

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            if (not receiver) or (not sender):
                return await self.send_json({"errors": {"receiver and sender": 'Fields are required!'}})

            messages = await get_messages_by_chat(sender, receiver, chat_id)

            return await self.send_data({"data": messages})

        elif action == 'send-message':
            user_id = content.pop('receiver', False)
            receiver = await self.get_receiver(user_id)

            sender = self.scope.get("user")

            content["sender"] = sender.id
            content['receiver'] = receiver.id

            chat_id = sorted([receiver.id, sender.id])

            await create_msg(content, user.id)

            await update_messages(sender.id, receiver.id, chat_id)

            users = await get_all_users(sender.id)

            await self.channel_layer.group_send(
                f"chatlist_{sender.id}",
                {
                    "type": "send.data",
                    "data": {'users': users}
                }
            )

            users = await get_all_users(receiver.id)

            await self.channel_layer.group_send(
                f"chatlist_{receiver.id}",
                {
                    "type": "send.data",
                    "data": {'users': users}
                }
            )

        elif action == "edit":
            message_id = content["msg_id"]
            text = content["text"]

            msg = await get_key_query(Message, message_id)
            msg.text = text
            await update_key_query(msg)

            sender = self.scope.get("user")
            receiver = content["receiver"]
            chat_id = sorted([receiver, sender.id])

            await update_messages(sender.id, receiver, chat_id)

            users = await get_all_users(sender.id)

            await self.channel_layer.group_send(
                f"chatlist_{sender.id}",
                {
                    "type": "send.data",
                    "data": {'users': users}
                }
            )

            users = await get_all_users(receiver)

            await self.channel_layer.group_send(
                f"chatlist_{receiver}",
                {
                    "type": "send.data",
                    "data": {'users': users}
                }
            )

        elif action == "delete":
            message_id = content["msg_id"]

            sender = self.scope.get("user")
            receiver = content["receiver"]
            chat_id = sorted([receiver, sender.id])
            await delete_key_query(Message, message_id)

            await update_messages(sender.id, receiver, chat_id)

            users = await get_all_users(sender.id)

            await self.channel_layer.group_send(
                f"chatlist_{sender.id}",
                {
                    "type": "send.data",
                    "data": {'users': users}
                }
            )

            users = await get_all_users(receiver)

            await self.channel_layer.group_send(
                f"chatlist_{receiver}",
                {
                    "type": "send.data",
                    "data": {'users': users}
                }
            )

        elif action == 'mark-as-read':

            sender = self.scope.get("user")
            receiver = content["receiver"]
            chat_id = sorted([receiver, sender.id])

            sorted_id = f"{chat_id[0]}{chat_id[1]}"

            kwargs = {
                "chat_id": sorted_id,
                "sender__id": receiver,
                "is_read": False
            }

            messages = await filterMessages(Message, kwargs)
            print(messages)
            for object in messages:
                msg = await get_key_query(Message, object["id"])
                msg.is_read = True
                await update_key_query(msg)

            await update_messages(sender.id, receiver, chat_id)

            users = await get_all_users(sender.id)

            await self.channel_layer.group_send(
                f"chatlist_{sender.id}",
                {
                    "type": "send.data",
                    "data": {'users': users}
                }
            )

            users = await get_all_users(receiver)

            await self.channel_layer.group_send(
                f"chatlist_{receiver}",
                {
                    "type": "send.data",
                    "data": {'users': users}
                }
            )

        #     chat_id = content.pop('chat_id', False)
        #     if not chat_id:
        #         return await self.send_json({"errors": {"chat_id": 'This field is required!'}})
        #     result = await mark_as_read_chat_messages(user, chat_id)
        #     await response.update(result)

        # elif action == 'mark-as-read-message':
        #     chat_id = content.pop('chat_id', False)
        #     message_id = content.pop('message_id', False)

        #     if not chat_id:
        #         return await self.send_json({"errors": {"chat_id": 'This field is required!'}})

        #     if not message_id:
        #         return await self.send_json({"errors": {"message_id": 'This field is required!'}})

        #     result = await mark_as_read_chat_messages(user, chat_id)
        #     await response.update(result)

        # return await self.send_message({"data": response})

    async def send_sender(self, event):
        text = event['text']
        return await self.send_json(text)

    async def send_receiver(self, event):
        text = event['text']
        return await self.send_json(text)

    async def send_data(self, event):
        data = event['data']
        return await self.send_json(data)

    @database_sync_to_async
    def get_receiver(self, id):

        receiver = User.objects.get(id=id)
        return receiver

    async def disconnect(self, code):
        user = self.scope.get('user', False)
        try:
            user.is_online = False
            user.last_online = datetime.now()
            await update_key_query(user)

            message = {
                "is_online": user.is_online,
                "last_online": datetime.strftime(user.last_online, '%Y-%m-%d %H:%M')
            }

            await self.channel_layer.group_send(
                f"user_online_{user.id}",
                {
                    "type": "send.data",
                    "data": message,
                }
            )
            if not user.is_anonymous:

                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
        except:
            pass
        finally:
            self.send(text_data=json.dumps(
                {'status': "Websocket disconnected"}))
            return await super().disconnect(code)
