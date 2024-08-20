from accounts.views import (
    CreatePupilAdmin, CreateTeacherAdmin, PhoneNumberView, RegisterUserView, 
    ResetPasswordVerifyCode, TeacherAndPupilDetailAdmin, VerifyCodeView, 
    HistoryUserView, ChangePasswordView, ResetPasswordView, ResetPasswordConfirm, 
    UpdateProfileView, UsersStatsList, ChangePhoneView, ChangePhoneVerifyCode,# LogoutView
    LoginTokenView, RefreshTokenView,
    )
from django.urls import path



urlpatterns = [
    path('login/token/', LoginTokenView.as_view()),
    path('login/token/refresh/', RefreshTokenView.as_view()),

    # path('logout/', TokenBlacklistView.as_view()),
    # path('logout/', LogoutView.as_view()),

    path('register/phone/', PhoneNumberView.as_view()),
    path('register/phone/verify/', VerifyCodeView.as_view()),
    path('register/user/', RegisterUserView.as_view()),

    path('user-history/', HistoryUserView.as_view()),

    # change user password
    path('password/change/', ChangePasswordView.as_view()),

    #reset user password
    path('password/reset/', ResetPasswordView.as_view()),
    path('password/reset/verify/code/', ResetPasswordVerifyCode.as_view()),
    path('password/reset/confirm/', ResetPasswordConfirm.as_view()),

    path('user/profile/', UpdateProfileView.as_view()),

    #change user phone number
    path('user/phone-number/change/', ChangePhoneView.as_view()),
    path('user/phone-number/change/verify-code/', ChangePhoneVerifyCode.as_view()),

    path('users-statistics/', UsersStatsList.as_view()),

    # admin
    path('admin/teacher/', CreateTeacherAdmin.as_view()),
    path('create/pupil/', CreatePupilAdmin.as_view()),
    path('admin/teacher-pupil/<int:pk>/', TeacherAndPupilDetailAdmin.as_view()),
]

