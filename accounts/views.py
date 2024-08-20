from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from rest_framework.permissions import AllowAny,  IsAdminUser, IsAuthenticated

from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import get_user_model
from random import randint
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
import datetime as d
import pytz
from accounts.models import HistoryOfEntries, Profile, Verification
from accounts.serializers import (
    ChangePasswordSerializer, ChangePhoneSerializer, HistorySerializer, PhoneSerializer, RefreshTokenSerializer,
    ResetPasswordSerializer, UserSerializer, VerifyCodeSerializer,
    RegisterUserSerializer, UpdateProfileSerializer
)
from course.models import Course
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from rest_framework import parsers




User = get_user_model()

utc = pytz.timezone(settings.TIME_ZONE)


def send_sms(phone_number, step_reset=None, change_phone=None):
    try:
        verify_code = randint(111111, 999999)
        try:
            obj = Verification.objects.get(phone_number=phone_number)
        except Verification.DoesNotExist:
            obj = Verification(phone_number=phone_number, verify_code=verify_code)
            obj.step_reset=step_reset 
            obj.step_change_phone=change_phone
            obj.save()
            context = {'phone_number': str(obj.phone_number), 'verify_code': obj.verify_code,
                       'lifetime': _('2 minutes')}
            return context
        time_now = d.datetime.now(utc)
        diff = time_now - obj.created
        two_minute = d.timedelta(minutes=1)
        if diff <= two_minute:
            time_left = str(two_minute - diff)
            return {'message': _(f"Try again in {time_left[3:4]} minute {time_left[5:7]} seconds")}
        obj.delete()
        obj = Verification(phone_number=phone_number)
        obj.verify_code=verify_code 
        obj.step_reset=step_reset
        obj.step_change_phone=change_phone
        obj.save()
        context = {'phone_number': str(obj.phone_number), 'verify_code': obj.verify_code, 'lifetime': _('2 minutes')}
        return context
    except Exception as e:
        print(f"\n[ERROR] error in send_sms <<<{e}>>>\n")

import requests
class PhoneNumberView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PhoneSerializer

    @swagger_auto_schema(request_body=PhoneSerializer, tags=['accounts'])
    def post(self, request):
        try:
            serializer = PhoneSerializer(data=request.data)
            if serializer.is_valid():
                phone_number = request.data['phone_number']
                v_code = send_sms(phone_number)
                if v_code is not None:
                    try:
                            sms = requests.post("http://sms-service.m1.uz/send_sms/", {"phone_number":v_code['phone_number'], \
                                                            "text":f"Sizning coursefy.org sayti uchun tasdiqlash kodingiz.\nDiqqat!\nBuni \
                                                             hech kimga bermang!\nKOD: {v_code['verify_code']}"})
                            response = sms.json()
                            return Response({"msg":response["msg"]}, status=status.HTTP_208_ALREADY_REPORTED)
                    except:
                        return Response({"msg":v_code["message"]}, status=status.HTTP_208_ALREADY_REPORTED)

                return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"\n[ERROR] <<<{e}>>>\n")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyCodeView(APIView):
    serializer_class = VerifyCodeSerializer
    permission_classes = [AllowAny]
    queryset = Verification.objects.all()

    @swagger_auto_schema(request_body=VerifyCodeSerializer, tags=['accounts'])
    def put(self, request, *args, **kwargs):
        data = request.data
        try:
            obj = Verification.objects.get(phone_number=data['phone_number'], verify_code=data['verify_code'])
            serializer = VerifyCodeSerializer(instance=obj, data=data)
            if serializer.is_valid():
                serializer.save()
                if serializer.data['step_change_phone'] == 'confirmed':
                    user = request.user
                    user.phone_number = data['phone_number']
                    user.save()
                    return Response({'message': 'Your phone number has been successfully changed!'},
                                status=status.HTTP_202_ACCEPTED)
                return Response({'message': 'This phone number has been successfully verified!'},
                                status=status.HTTP_202_ACCEPTED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Verification.DoesNotExist:
            return Response({'error': 'Phone number or verify code incorrect!'}, statusis_pupil=status.HTTP_400_BAD_REQUEST)


class RegisterUserView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterUserSerializer
    queryset = User.objects.all()
    my_tags = ['accounts']

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        phone_number = serializer.data['phone_number']
        user = User.objects.get(phone_number=phone_number)
        access_token = AccessToken().for_user(user)
        refresh_token = RefreshToken().for_user(user)
        return Response({
            "access": str(access_token),
            "refresh": str(refresh_token),
            **serializer.data
        })


class CreateTeacherAdmin(generics.CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = RegisterUserSerializer
    queryset = User.objects.all()
    my_tags = ['admin']

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request, 'is_teacher': True})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeacherAndPupilDetailAdmin(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = RegisterUserSerializer
    queryset = User.objects.all()
    my_tags = ['admin']

    def get(self, request, pk):
        user = self.get_object(pk)
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(request_body=RegisterUserSerializer)
    def patch(self, request, pk):
        user = self.get_object(pk)
        serializer = self.serializer_class(instance=user, data=request.data, context={'request': request, 'is_teacher': True})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        user = self.get_object(pk)
        user.delete()
        return Response({'msg': 'Successfully deleted!'}, status=status.HTTP_204_NO_CONTENT)

    def get_object(self, pk):
        try:
            return User.objects.get(id=pk)
        except User.DoesNotExist:
            raise Http404


class CreatePupilAdmin(CreateTeacherAdmin):
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request, 'is_pupil': True})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = ChangePasswordSerializer
    my_tags = ['accounts']

    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def put(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(instance=self.request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'msg': 'Password successfully updated'}, status=status.HTTP_200_OK)


class ChangePhoneView(APIView):
    serializer_class = ChangePhoneSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    my_tags = ['accounts']

    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ChangePhoneSerializer)
    def patch(self, request):
        data = request.data
        user = request.user
        serializer = self.serializer_class(instance=user, data=data)
        serializer.is_valid(raise_exception=True)
        phone_number = data.get('phone_number', False)
        parent_phone_number = data.get('parent_phone_number', False)
        if parent_phone_number:
            profile = user.profile
            profile.parent_phone_number = parent_phone_number
            profile.save()
        if phone_number:
            user = self.queryset.filter(phone_number__iexact=phone_number)
            if user.exists():
                return Response({'error': 'this phone_number already exist!'}, status=status.HTTP_400_BAD_REQUEST)
            v_code = send_sms(request.data['phone_number'], change_phone='send')
            if v_code is not None:
                try:
                        sms = requests.post("http://sms-service.m1.uz/send_sms/", {"phone_number":v_code['phone_number'], \
                                                        "text":f"Sizning coursefy.org sayti uchun tasdiqlash kodingiz.\nDiqqat!\nBuni \
                                                         hech kimga bermang!\nKOD: {v_code['verify_code']}"})
                        response = sms.json()
                        return Response({"msg":response["msg"]}, status=status.HTTP_208_ALREADY_REPORTED)
                except:
                    return Response({"msg":v_code["message"]}, status=status.HTTP_208_ALREADY_REPORTED)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class ChangePhoneVerifyCode(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VerifyCodeSerializer
    queryset = Verification.objects.all()
    my_tags = ['accounts']

    @swagger_auto_schema(request_body=VerifyCodeSerializer, tags=['accounts'])
    def post(self, request):
        data = request.data
        try:
            obj = Verification.objects.get(phone_number=data['phone_number'])
            serializer = VerifyCodeSerializer(instance=obj, data=data)
            if serializer.is_valid():
                serializer.save()
                if serializer.data['step_change_phone'] == 'confirmed':
                    user = request.user
                    user.phone_number = data['phone_number']
                    user.save()
                    return Response({'message': 'Your phone number has been successfully changed!'},
                                status=status.HTTP_202_ACCEPTED)
                return Response({'message': 'This phone number has been successfully verified!'},
                                status=status.HTTP_202_ACCEPTED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Verification.DoesNotExist:
            return Response({'error': 'Phone number or verify code incorrect!'}, status=status.HTTP_400_BAD_REQUEST)

#Password Reset
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PhoneSerializer

    @swagger_auto_schema(request_body=PhoneSerializer, tags=['accounts'])
    def post(self, request):
        try:
            User.objects.get(phone_number=request.data['phone_number'])
            v_code = send_sms(request.data['phone_number'], step_reset='send')
            if v_code is not None:
                try:
                        sms = requests.post("http://sms-service.m1.uz/send_sms/", {"phone_number":v_code['phone_number'], \
                                                        "text":f"Sizning coursefy.org sayti uchun tasdiqlash kodingiz.\nDiqqat!\nBuni \
                                                         hech kimga bermang!\nKOD: {v_code['verify_code']}"})
                        response = sms.json()
                        return Response({"msg":response["msg"]}, status=status.HTTP_208_ALREADY_REPORTED)
                except:
                    return Response({"msg":v_code["message"]}, status=status.HTTP_208_ALREADY_REPORTED)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordVerifyCode(VerifyCodeView):
    my_tags = ['accounts']


class ResetPasswordConfirm(APIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer
    my_tags = ['accounts']

    @swagger_auto_schema(request_body=ResetPasswordSerializer)
    def put(self, request, *args, **kwargs):
        try:
            user = User.objects.get(phone_number=request.data['phone_number'])
        except:
            return Response({'error': "User matching query doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ResetPasswordSerializer(instance=user, data=request.data)
        if serializer.is_valid():
            ver = Verification.objects.get(phone_number=request.data['phone_number'])
            if ver.step_reset == 'confirmed':
                user.set_password(request.data['new_password'])
                ver.step_reset = ''
                ver.save()
                user.save()
                return Response({'message': 'Password successfully updated'}, status=status.HTTP_200_OK)
            return Response({'error': f'First get verify code, then reset password!'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HistoryUserView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HistorySerializer

    @swagger_auto_schema(tags=['user'])
    def get(self, request):
        histories = HistoryOfEntries.objects.filter(user=request.user.id)
        serializer = HistorySerializer(histories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateProfileView(generics.RetrieveUpdateAPIView):
        permission_classes = [IsAuthenticated]
        serializer_class = UpdateProfileSerializer
        parser_classes = (parsers.MultiPartParser, parsers.FileUploadParser, parsers.FormParser)
        queryset = Profile.objects.all()
        my_tags = ['user']

        def get_object(self):
            return Profile.objects.get_or_create(user=self.request.user)[0]

         


class UsersStatsList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    my_tags = ['landing-page']

    def get(self, request):
        total_users = self.queryset.count()
        total_teachers = User.objects.filter(groups__name='Teacher').count()
        total_courses = Course.objects.count()
        return Response(
                        {
                            'total_users': total_users,
                            'total_teachers': total_teachers,
                            'total_courses': total_courses
                        }, status=status.HTTP_200_OK

                    )
                    
from accounts.custom_token import TokenObtainPairVieww

class LoginTokenView(TokenObtainPairVieww):
    my_tags = ['accounts']



class RefreshTokenView(TokenRefreshView):
    my_tags = ['accounts']


# class LogoutView(APIView):
#     permission_classes = [IsAuthenticated]
#     my_tags = ['accounts']

#     @swagger_auto_schema(request_body=TokenBlacklistSerializer)
#     def post(self, request):
#         token = RefreshToken(request.data.get('refresh'))
#         token.blacklist()
#         return Response({"message": "User logged out!"}, status=status.HTTP_202_ACCEPTED)
