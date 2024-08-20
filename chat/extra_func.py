from chat.models import Message
from django.contrib.auth import get_user_model
import math
from chat.models import Message
from chat.serializers import MessageSerializer,  ListChatSerializer
from django.db.models import Q
from asgiref.sync import sync_to_async
from .serializers import UserSerializer

User = get_user_model()

@sync_to_async
def get_messages_by_chat(sender, receiver, sorted_list):

    chat_id = f"{sorted_list[0]}{sorted_list[1]}"
    messages = Message.objects.filter(chat_id = chat_id).order_by('id')

    serializer = MessageSerializer(messages, many=True, context = {"receiver":receiver})

    return {
            "result": serializer.data
           }

@sync_to_async
def get_chats_by_user(user):
    msgs = Message.objects.filter(Q(sender=user) | Q(receiver=user))  # "postgre"ga o'tganda distinct() funksiyasi bilan bundan keyingi 5 qator kod  qisqaradi
    d = {}
    for msg in msgs:

        if msg.chat_id not in d.values():
            d[msg.id] = msg.chat_id
    chats = msgs.filter(id__in=d.keys())

    serializer = ListChatSerializer(chats, many=True)
    return serializer.data


@sync_to_async
def get_chat_users(user):
    users = User.objects.all()
    ls = []
    try:
        for u in users:
            us = {}
            if u != user:
                ids = sorted([u.id, user.id])
                chat_id = int(str(ids[0])+str(ids[1]))
                # if Message.objects.filter(Q(sender=u) | Q(receiver=u)) or Message.objects.filter(Q(sender=u) | Q(receiver=u)):
                if Message.objects.filter(chat_id=chat_id):
                    us['id'] = u.id
                    p = str(u.phone_number)
                    us['phone_number'] = p
                    # if u.profile:
                    #     us['first_name'] = str(u.profile.first_name)
                    #     us['last_name'] = str(u.profile.last_name)
                    #     us['middle_name'] = str(u.profile.middle_name)
                    #     p = str(u.profile.parent_phone_number)
                    #     us['parent_phone_number'] = p
                    #     us['birth_date'] = str(u.profile.birth_date)
                    #     us['language'] = str(u.profile.language)
                    # if u.profile.image:
                        # im = u.profile.images
                        # print(type(im))
                        # us['image'] = im
                    ls.append(us)
        return ls
    except:
        return ls
   

@sync_to_async
def get_all_users(user):
    users = User.objects.all().order_by("sender_messages__create_at", "receiver_messages__created_at")

    users_l = []

    for i in users:
        if i not in users_l:
            users_l.append(i)
    
    serializer = UserSerializer(users_l, many = True, context = {"user":user})

    return serializer.data


@sync_to_async
def mark_as_read_chat_messages(user, chat_id):
    try:
        messages = Message.objects.filter(Q(sender=user) | Q(receiver=user), chat_id=chat_id, is_read=False)
        if messages:
            messages.update(is_read=True)
        return {'result': 'ok'}
    except:
        return {'result': 'Server error'}


@sync_to_async
def mark_as_read_chat_messages(user, chat_id, message_id):
    try:
        messages = Message.objects.filter(Q(sender=user) | Q(receiver=user), chat_id=chat_id, id__lte=message_id)
        if messages:
            messages.update(is_read=True)
            messages.save()
        return {'result': 'ok'}
    except:
        return {'result': 'Server error'}
    

# @sync_to_async
# def create_msg(content, user, receiver):
#     content['receiver'] = receiver
#     serializer = MessageSerializer(data=content, context={'files': False, 'user': user})
#     print(serializer.is_valid())
#     if serializer.is_valid():
#         serializer.save()
#         print('SER.DATA',serializer.data)
#         return serializer.data
#     return serializer.errors

@sync_to_async
def create_msg(content, user):
    reply_id = content["reply_id"]
    receiver = content["receiver"]
    serializer = MessageSerializer(data=content, context={'user':user, "receiver":receiver, "reply_id": reply_id})

    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return serializer.data
    else:
        return {}