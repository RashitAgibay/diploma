from django.urls import re_path
from .views import *
app_name = 'users'

urlpatterns = [
    re_path(r'registration/', CreateUser.as_view()),
    re_path(r'validate_user_phone/', ValidateUserPhoneOTP.as_view()),
    re_path(r'profile/', UserProfile.as_view()),
    re_path(r'resend/', ResendOTP.as_view()),
    re_path(r'forgot_password/', UserForgotPassword.as_view()),
    re_path(r'get_info/', UserInfo.as_view()),
    re_path(r'city/', UserGeoView.as_view()),
]