from asyncore import read
from multiprocessing import context
from rest_framework import serializers
from chat.models import Message, MessageFile
from accounts.serializers import ChatUserProfileSerializer
# from django.contrib.auth import get_user_model
from accounts.models import User, Profile
import datetime


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = (
            'picture',
            'first_name',
            'last_name',
            'middle_name',
            'parent_phone_number',
            'birth_date',
            'language',
            'created',
            'updated'
        )


class MessageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageFile
        fields = (
            'id',
            'file',
        )


class MessageSerializer(serializers.ModelSerializer):
    files = MessageFileSerializer(many=True, required=False)
    # created_at = seri alizers.DateTimeField(format = "%D-%m-%Y %H:%M:%S")
    is_receiver = serializers.SerializerMethodField(read_only=True)
    reply_id = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            'id', 'sender', 'receiver',
            'text', 'chat_id', 'reply_id',
            'is_read', 'files', 'created_at', "is_receiver"
        )
        extra_kwargs = {
            'chat_id': {'read_only': True},
            'sender': {'read_only': True},
            'is_read': {'read_only': True},
        }

    def get_reply_id(self, obj):
        if obj.reply_id is not None:
            reply_message = Message.objects.get(id=obj.reply_id.id)
            receiver = self.context["receiver"]
            if reply_message.sender.id != receiver:
                is_receiver = False
            else:
                is_receiver = True
            data = {
                "id": reply_message.id,
                "message": reply_message.text,
                "is_receiver": is_receiver
            }

            return data
        else:
            return None

    def get_is_receiver(self, obj):
        receiver = self.context["receiver"]
        if obj.sender.id != receiver:
            return False
        else:
            return True

    def to_representation(self, instance):
        representation = super(
            MessageSerializer, self).to_representation(instance)
        # representation['profile'] = ChatUserProfileSerializer(instance.receiver.profile).data
        # representation['files'] = MessageFileSerializer(instance.msg_files.all(), many=True).data
        return representation

    def validate(self, attrs):
        super().validate(attrs)
        sender = self.context.get('user', False)
        receiver = attrs['receiver']
        attrs["reply_id"] = self.context.get('reply_id', None)
        if sender == receiver:
            raise serializers.ValidationError(
                {'receiver': "The user self-messaging function is not currently available"})
        # r_files = self.context.get('files', False)
        text = attrs.get('text', False)
        # if not text and len(r_files) < 1:
        if not text:
            raise serializers.ValidationError({'text': 'This is required'})
        return attrs

    def create(self, validated_data):
        try:
            user = self.context.get('user', False)
            sender = User.objects.get(id=user)
            receiver = validated_data['receiver']
            text = validated_data.get('text', False)
            reply_id = validated_data.get('reply_id', None)
            ids = sorted([sender.id, receiver.id])
            chat_id = int(str(ids[0])+str(ids[1]))
            # # r_files = self.context.get('files', False)

            message = Message(
                sender=sender, receiver=receiver, chat_id=chat_id)
            if reply_id is not None:
                reply_message = Message.objects.get(id=reply_id)
                message.reply_id = reply_message
            if text:
                message.text = text
            message.save()
            # if r_files:
            #     files = r_files.pop('files')
            #     lst_files = [MessageFile(message=message, file=file) for file in files]
            #     MessageFile.objects.bulk_create(lst_files)
            return message
        except Exception as e:
            # print(e)
            raise serializers.ValidationError({'error': e})


class ChatListSerializer(MessageSerializer):
    def to_representation(self, instance):
        representation = super(
            MessageSerializer, self).to_representation(instance)
        if instance.sender == self.context.user:
            representation['profile'] = ChatUserProfileSerializer(
                instance.receiver.profile).data
        elif instance.receiver == self.context.user:
            representation['profile'] = ChatUserProfileSerializer(
                instance.sender.profile).data
        representation['new_msg'] = self.Meta.model.objects.filter(
            chat_id=instance.chat_id, is_read=False).count()
        representation['files'] = MessageFileSerializer(
            instance.msg_files.all(), many=True).data

        return representation


class ListChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('chat_id',)


class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def to_representation(self, instance):
        representation = super(
            ListUserSerializer, self).to_representation(instance)
        if instance.profile:
            representation['first_name'] = instance.profile.first_name
            representation['last_name'] = instance.profile.last_name
            representation['middle_name'] = instance.profile.middle_name
            representation['parent_phone_number'] = instance.profile.parent_phone_number
            representation['birth_date'] = instance.profile.birth_date
            representation['language'] = instance.profile.language
        if instance.profile.image:
            representation['image'] = instance.profile.image
        return representation


class UserSerializer(serializers.ModelSerializer):

    last_login = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")
    updated_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")

    last_message = serializers.SerializerMethodField(read_only=True)

    profile = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "last_login",
            "is_staff",
            "is_superuser",
            "is_active",
            "created_at",
            "updated_at",
            "is_online",
            "last_online",
            "profile",
            "last_message"
        )

    def get_profile(self, obj):
        profile = obj.profile
        serializer = ProfileSerializer(profile, many=False)
        return serializer.data

    def get_last_message(self, obj):
        try:
            user = self.context["user"]
            sorted_id = sorted([user, obj.id])
            chat_id = f"{sorted_id[0]}{sorted_id[1]}"
            message = Message.objects.filter(chat_id=chat_id).order_by(
                "created_at")[Message.objects.filter(chat_id=chat_id).count()-1]
        except Exception as e:
            return None

        if datetime.datetime.today().date() > message.created_at.date():
            message.created_at = message.created_at.strftime("%m/%d")
        else:
            message.created_at = message.created_at.strftime("%H:%M")

        serializer = MessageSerializer(
            message, many=False, context={"receiver": obj.id})

        # print(serializer.data["created_at"], "\n\n\n\n\n")

        return serializer.data
