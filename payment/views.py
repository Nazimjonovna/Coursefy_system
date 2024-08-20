from rest_framework import status
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.views import APIView
from payment.models import PaymentHistory
from rest_framework.permissions import IsAuthenticated
from payment.serializers import PaymentCourseSerializer, PaymentHistoryPupilSerializer, PaymentTestSerializer, PaymentHistoryAdminSerializer
from django.db.models import Q


def is_teacher(user):
    return user.groups.filter(name='Teacher').exists()


class PaymentHistoryAdminList(ListAPIView):
    serializer_class = PaymentHistoryAdminSerializer
    queryset = PaymentHistory.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    my_tags = ['admin']

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser:
            obj_list = self.queryset.all()
            serializer = self.serializer_class(obj_list, many=True)
            return super().get(request, *args, serializer.data)
        elif is_teacher(user):
            user_courses = user.courses.all()
            user_tests = user.author_tests.all()
            obj_list = self.queryset.filter(Q(course__in=user_courses) | Q(test__in=user_tests))
            serializer = self.serializer_class(obj_list, many=True)
            return super().get(request, *args, serializer.data)
        else:
            return Response({'msg': 'You are not teacher or admin'}, status=status.HTTP_404_NOT_FOUND)


class PaymentHistoryPupil(ListAPIView):
    serializer_class = PaymentHistoryPupilSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = PaymentHistory.objects.all()
    my_tags = ['user']

    def get_queryset(self):
        try:
            queryset = self.queryset.filter(user=self.request.user)
            return queryset
        except:
            pass


class PaymentCourseView(CreateAPIView):
    serializer_class = PaymentCourseSerializer
    queryset = PaymentHistory.objects.all()
    permission_classes = [IsAuthenticated]
    my_tags = ['payment']

    def post(self, request, *args, **kwargs):
        data = request.data
        ser = self.serializer_class(data=data)
        if ser.is_valid():
            course, user = data['course'], data['user']
            try:
                course = PaymentHistory.objects.get(user=user, course=course)
                if course is not None:
                    return Response({'msg': 'You have already purchased this course'},
                                    status=status.HTTP_400_BAD_REQUEST)
            except PaymentHistory.DoesNotExist:
                ser.save()
                return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentTestView(CreateAPIView):
    serializer_class = PaymentTestSerializer
    queryset = PaymentHistory.objects.all()
    permission_classes = [IsAuthenticated]
    my_tags = ['payment']

    def post(self, request, *args, **kwargs):
        data = request.data
        ser = self.serializer_class(data=data)
        if ser.is_valid():
            course, user = data['test'], data['user']
            try:
                course = PaymentHistory.objects.get(user=user, course=course)
                if course is not None:
                    return Response({'msg': 'You have already purchased this test'}, status=status.HTTP_400_BAD_REQUEST)
            except PaymentHistory.DoesNotExist:
                ser.save()
                return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class TestingPayment(APIView):
    my_tags = ['payment']
    def get(self, request):
        import requests
        url = "https://merchant/pay/" 
        payload='params%5Baccount%5D%5Bphone%5D=998760914&method=PerformTransaction&params%5Bid%5D=61d446b3294a641eee22b522&params%5Btime%5D=1399114284039&params%5Bamount%5D=5000'
        headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cache-Control': 'no-cache',
                'Authorization': 'Bearer XAGXmPBM9pgYi11VBiJ3VWr8TtGJotiC1FXf'
                }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)
