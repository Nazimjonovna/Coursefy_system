from django.http import Http404
from rest_framework import status, pagination
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from chat.models import Message
from chat.serializers import ChatListSerializer, MessageSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FileUploadParser
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ChatListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatListSerializer
    queryset = Message.objects.all()
    pagination_class = CustomPagination
    my_tags = ['chat']

    def get_queryset(self):
        try:
            user = self.request.user
            msgs = self.queryset.filter(Q(sender=user) | Q(receiver=user))  # "postgre"ga o'tganda distinct() funksiyasi bilan bundan keyingi 5 qator kod  qisqaradi
            d = {}
            for msg in msgs:
                if msg.chat_id not in d.values():
                    d[msg.id] = msg.chat_id
            queryset = msgs.filter(id__in=d.keys())
            return queryset
        except:
            pass

    def get_serializer_context(self):
        return self.request


class MessageCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    parser_classes = (MultiPartParser, FileUploadParser)
    my_tags = ['chat']

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'files': request.FILES, 'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def get_parsers(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().get_parsers()

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class MessageMarkAsRead(APIView):
    """
    ### ID beriladi va shu IDgacha bo'lgan barcha xabarlar o'qildi deb belgilanadi
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    my_tags = ['chat']

    def patch(self, request, pk):
        user = request.user
        msgs = self.queryset.filter(Q(sender=user) | Q(receiver=user), id__lte=pk)
        if msgs:
            msgs.update(is_read=True)
            msgs.save()
            return Response({'message': 'Messages successfully read!'}, status=status.HTTP_200_OK)
        return Response({'message': 'Messages already read'}, status=status.HTTP_400_BAD_REQUEST)


chat_id = openapi.Parameter('chat_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER)

class MessagesByChat(ListAPIView, APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    pagination_class = CustomPagination
    my_tags = ['chat']

    @swagger_auto_schema(manual_parameters=[chat_id])
    def get(self, request, *args, **kwargs):
        """
        ### chatdagi barcha xabarlarni olish uchun chat_id beriladi
        """
        chat_id = request.GET.get('chat_id', False)
        if not chat_id:
            return Response({'error': '\"chat_id\" is required'}, status=status.HTTP_400_BAD_REQUEST)
        #     messages = Message.objects.filter(chat_id=chat_id)
        #     if messages:
        #         serializer = self.serializer_class(messages, many=True)
        #         return Response(serializer.data, status=status.HTTP_200_OK)
        #     else:
        #         return Response({'message': 'Chat does not exist!'}, status=status.HTTP_404_NOT_FOUND)
        # else:
        #     return Response({'error': '\"chat_id\" is required'}, status=status.HTTP_400_BAD_REQUEST)
        return super().get(request, *args, **kwargs)
        
    def get_queryset(self):
        chat_id = self.request.GET.get('chat_id', False)
        return Message.objects.filter(chat_id=chat_id)
    
    @swagger_auto_schema(manual_parameters=[chat_id], request_body=None)
    def patch(self, request):
        """
        ### chat_id beriladi shu chatdagi barcha xabarlar o'qildi deb belgilanadi
        """
        chat_id = request.GET.get('chat_id', False)
        if chat_id:
            user = request.user
            messages = self.queryset.filter(Q(sender=user) | Q(receiver=user), chat_id=chat_id, is_read=False)
            if messages:
                messages.update(is_read=True)
                return Response({'message': 'Messages has been successfully read!'}, status=status.HTTP_200_OK)
            return Response({'message': 'Messages already read!'}, status=status.HTTP_208_ALREADY_REPORTED)
        else:
            return Response({'error': '\"chat_id\" is required'}, status=status.HTTP_400_BAD_REQUEST)

