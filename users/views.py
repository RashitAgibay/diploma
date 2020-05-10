from django.shortcuts import get_object_or_404
from project.custom_functions import api2_response
from .smsc_api import SMSC
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User, PhoneOTP
from .serializer import CreateUserSerializer, UserProfileSerializer, UserInfoSerializer
from django.http import JsonResponse
from unique.models import City
from images.models import Image
import random
import geoip2.database

smsc = SMSC()
""" 
r = smsc.get_sms_cost("77057007079", "Вы успешно зарегистрированы!")
r = smsc.send_sms("77057007079", "Ваш пароль: 123", sender="sms")
r = smsc.get_status(12345, "77057007079")
balance = smsc.get_balance()
# https://smsc.kz/sys/send.php?login=kupizalog&psw=04268390d4ab7741c5e7e461657344befb41204e&phones=77057007079&mes=
# Подтверждение на сайте www.kupizalog.kz 154684
"""


def send_otp(phone):
    if phone:
        key = random.randint(99999, 999999)
        if key and (key > 99999) and (key < 999999):
            r = smsc.send_sms("+7" + str(phone), "Подтверждение на сайте www.kupizalog.kz : " + str(key), sender="sms")
            if len(r) > 2:
                return key
            else:
                return False

    else:
        return False


class CreateUser(APIView):
    status_code = status.HTTP_200_OK
    detail = "Объявление добавлен"
    data = {}
    safe = True

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        password1 = request.data.get('password1')
        password2 = request.data.get('password2')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        validated = True
        message = ""
        if not phone:
            validated = False
            message = message + 'Требуется номер телефона! '

        user = User.objects.filter(phone__iexact=phone)
        if user.exists():
            validated = False
            message = message + 'Пользователь с таким номером телефона уже существует! '

        if not (password2 and password1 and (password1 == password2)):
            validated = False
            message = message + 'Пароли должны совпадать, пожалуйста, введите тот же пароль '

        if not (first_name and last_name):
            validated = False
            message = message + 'Требуется имя и фамилия!'
        if not validated:
            if request.version == 'v2':
                self.data = {}
                self.detail = message
                self.status_code = status.HTTP_400_BAD_REQUEST
                return api2_response(self)
            return Response({
                'status': False,
                'detail': message
            })

        image = Image.objects.get(id=122)
        temp_data = {
            'phone': phone,
            'password': password1,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'is_active': False,
        }
        serializer = CreateUserSerializer(data=temp_data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.active = False
        user.image = image
        user.save()
        phone_otp_key = send_otp(phone)
        if phone_otp_key:
            PhoneOTP.objects.create(
                phone=phone,
                otp=phone_otp_key
            ).save()
            message = 'Код подтверждения(OTP code) успешно отправлен на ваш номер'
            if request.version == 'v2':
                self.data = {}
                self.detail = message
                self.status_code = status.HTTP_201_CREATED
                return api2_response(self)
            return Response({
                'status': True,
                'detail': message
            })
        else:
            user.delete()
            message = message + 'Ошибка при отправке кода для подтверждении(OTP code)!'
            if request.version == 'v2':
                self.data = {}
                self.detail = message
                self.status_code = status.HTTP_400_BAD_REQUEST
                return api2_response(self)
            return Response({
                'status': False,
                'detail': message
            })


class ResendOTP(APIView):
    status_code = status.HTTP_200_OK
    detail = "Сообщение с кодом подтверждение отправлена"
    data = {}
    safe = True

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        if phone:
            phone_otp = PhoneOTP.objects.filter(phone=phone)
            if phone_otp.exists():
                phone_otp = phone_otp.first()
                resent_count = phone_otp.resent_count
                if resent_count > 4:
                    phone_otp.validate = True
                    phone_otp.save()
                    if request.version == 'v2':
                        self.data = {}
                        self.detail = "Ваш аккаунт заблокирован обратитесь на службу поддержки сайта."
                        self.status_code = status.HTTP_406_NOT_ACCEPTABLE
                        return api2_response(self)
                    return Response({
                        'status': False,
                        'detail': "Ваш аккаунт заблокирован обратитесь на службу поддержки сайта."
                    })
                otp_key = send_otp(phone)
                if otp_key:
                    phone_otp.otp = otp_key
                    phone_otp.resent_count = resent_count + 1
                    phone_otp.save()
                    if request.version == 'v2':
                        self.data = {}
                        self.detail = "Сообщение отправлен на номер +7%s ,Попыток осталось : %d ." % (
                            phone, 5 - resent_count)
                        self.status_code = status.HTTP_201_CREATED
                        return api2_response(self)
                    return Response({
                        'status': True,
                        'detail': "Сообщение отправлен на номер +7%s ,Попыток осталось : %d ." % (
                            phone, 5 - resent_count),
                    })
                else:
                    if request.version == 'v2':
                        self.data = {}
                        self.detail = "Не удалось отправить сообщение,Попробуйте позже или " \
                                      "обратитесь на службу поддержки сайта."
                        self.status_code = status.HTTP_400_BAD_REQUEST
                        return api2_response(self)
                    return Response({
                        'status': False,
                        'detail': "Не удалось отправить сообщение,Попробуйте позже или "
                                  "обратитесь на службу поддержки сайта."
                    })
            else:
                if request.version == 'v2':
                    self.data = {}
                    self.detail = "Сначало пройдите Регистрация."
                    self.status_code = status.HTTP_401_UNAUTHORIZED
                    return api2_response(self)
                return Response({
                    'status': False,
                    'detail': "Сначало пройдите Регистрация."
                })
        else:
            if request.version == 'v2':
                self.data = {}
                self.detail = "Для повторной отправки передайте Номер телефона"
                self.status_code = status.HTTP_208_ALREADY_REPORTED
                return api2_response(self)
            return Response({
                'status': False,
                'detail': "Для повторной отправки передайте Номер телефона"
            })


class UserForgotPassword(APIView):
    """
    Phone (10 last digits ) Required for all request

    resend - Boolean, Default False, If True is Resent OTP, when user want to resend code

    otp - Number or None, if filled code it means to confirm OTP, and checks them.

    Password1 , Requirements is Validate OTP.
    Password2
    IF has password1, password2 and Validated OTP : password will be change
    """
    status_code = status.HTTP_200_OK
    detail = "Сообщение с кодом подтверждение отправлена"
    data = {}
    safe = True
    status_bool = True

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        resend = request.data.get('resend')
        get_object_or_404(User, phone=phone)
        if resend:
            resend_otp = ResendOTP()
            return resend_otp.post(request, *args, **kwargs)
        if phone:
            phone_otp = PhoneOTP.objects.filter(phone=phone)
            if phone_otp.exists():
                phone_otp = phone_otp.first()
                otp_key = phone_otp.otp
                otp_sent = request.data.get('otp')
                if otp_sent:
                    if str(otp_key) == str(otp_sent):
                        phone_otp.validate = True
                        phone_otp.save()
                        self.status_bool = True
                        self.detail = 'Теперь придумайте новый пароль'
                    else:
                        otp_send_count = phone_otp.count
                        phone_otp.count = otp_send_count + 1
                        phone_otp.save()
                        self.status_bool = False
                        self.detail = 'Повтарите попытку или переотправьте код подтверждение'
                else:
                    if not phone_otp.validate:
                        self.status_bool = False
                        self.detail = 'Сначало подтвердите что вы владелец аккаунта, Подтвердите ваш номер!'
                    else:
                        password1 = request.data.get('password1')
                        password2 = request.data.get('password2')
                        if password1 == password2 and password1 and password2:
                            User.objects.password_change(phone, password1)
                            phone_otp.delete()
                            self.status_bool = True
                            self.detail = 'Пароль изменено переходите на логин'
                        else:
                            self.status_bool = False
                            self.detail = 'Пароли не совпадают повторите попытку'
            else:
                otp_key = send_otp(phone)
                if otp_key:
                    PhoneOTP.objects.create(
                        phone=phone,
                        otp=otp_key,
                        forgot=True,
                    ).save()
                    # todo before Realise
                    self.status_bool = True
                    self.detail = "Код подтверждение отправлен на ваш номер"
                else:
                    self.status_bool = False
                    self.detail = "Не удалось отправить сообщение,Попробуйте позже или " \
                                  "обратитесь на службу поддержки сайта."
        else:
            self.status_bool = False
            self.detail = "Номер телефона обязательная поля"
        if request.version == 'v2':
            if not self.status_bool:
                self.status_code = status.HTTP_400_BAD_REQUEST
            return api2_response(self)
        return Response({
            'status': self.status_bool,
            'detail': self.detail
        })


class ValidateUserPhoneOTP(APIView):
    """
        Verification phone number of user
        Post :
            Required:
                phone : digit with length 10 - 7077777777
                otp : is 6 digits (sms code)
            Returns:
                'status': True,
                'detail': 'Info in bad english)'

        """
    status_code = status.HTTP_200_OK
    detail = "Код совпадает, пожалуйста, перенаправьте на логин. Номер телефона успешно подтвержден!"
    data = {}
    safe = True
    status_bool = True

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone', False)
        otp_sent = request.data.get('otp', False)
        if phone and otp_sent:
            old = PhoneOTP.objects.filter(phone__iexact=phone)
            if old.exists():
                old = old.first()
                otp = old.otp
                if str(otp) == str(otp_sent):
                    old.validate = True
                    user = User.objects.filter(phone=phone)
                    user = user.first()
                    user.active = True
                    user.save()
                    old.delete()
                else:
                    self.status_bool = False
                    self.detail = "Введен неправильный код"
            else:
                self.status_bool = False
                self.detail = "Сначала необходимо отправить код"
        else:
            self.status_bool = False
            self.detail = "Номер телефона обязательная поля"

        if request.version == 'v2':
            if not self.status_bool:
                self.status_code = status.HTTP_400_BAD_REQUEST
            return api2_response(self)
        return Response({
            'status': self.status_bool,
            'detail': self.detail
        })


class UserProfile(APIView):
    """
        + POST Method For get users info
        Required :
        --access_token

        + PUT method For Change
        Required :
        --access_token
        Not required:
        --Email( from Settings in User Profile)
        --City( Id of City from MainPage(set city) )
        --Phone(to change phone number of user, for verify sent with phone_otp(code))
        --phone_otp(after sending phone(without phone_otp) to sent OTP, and it is for verify and change it to new phone)
        --password(if match with old password, compares password1 and password2 then changes password)
        --password1( must match with pass2)
        --password2
        -- Not working Image (to sent Image)

    """
    status_code = status.HTTP_200_OK
    detail = 'Все изменении обновлены'
    data = {}
    safe = True
    status_bool = True

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserProfileSerializer(user)
        if request.version == 'v2':
            self.data = serializer.data
            self.safe = False
            return api2_response(self)
        return JsonResponse(serializer.data, safe=False)

    def put(self, request, *args, **kwargs):
        user = request.user
        # change or set user email
        if request.data.get('email'):
            user.email = request.data.get('email')
        # Change City or set city
        if request.data.get('city'):
            user.city = City.objects.get(id=request.data.get('city'))
        if request.data.get('first_name'):
            user.first_name = request.data.get('first_name')
        if request.data.get('last_name'):
            user.last_name = request.data.get('last_name')
        image = list(request.FILES.values())
        if image:
            current_image = Image.objects.create(unique=user.unique, path=image[0])
            current_image.save()
            user.image = current_image
        user.save()
        # change user's username -> phone
        if request.data.get('phone'):
            phone = request.data.get('phone')
            need_send_otp = True
            if request.data.get('phone_otp'):
                phone_otp = request.data.get('phone_otp')
                old = PhoneOTP.objects.filter(phone__iexact=phone)
                if old.exists():
                    need_send_otp = False
                    old = old.first()
                    otp = old.otp
                    if str(otp) == str(phone_otp):
                        old.validate = True
                        user.phone = phone
                        user.save()
                        old.delete()
                        self.status_bool = True
                        self.detail = 'Номер успешно изменен!'
                    else:
                        self.status_bool = False
                        self.detail = 'Код подтверждения не совпадает, Попробуйте еще раз или Перенаправьте код!'
            if need_send_otp:
                phone_otp_key = send_otp(phone)
                if phone_otp_key:
                    PhoneOTP.objects.create(
                        phone=phone,
                        otp=phone_otp_key
                    ).save()
                    # todo before Realise
                    self.status_bool = True
                    self.detail = 'Код подтверждения(OTP code) успешно отправлен на ваш номер'
                else:
                    self.status_bool = False
                    self.detail = "Ошибка при отправке смс"
            if request.version == 'v2':
                if not self.status_bool:
                    self.status_code = status.HTTP_400_BAD_REQUEST
                return api2_response(self)
            return Response({
                'status': self.status_bool,
                'detail': self.detail
            })

        if request.data.get('password'):
            if user.check_password(request.data.get('password')):
                password1 = request.data.get('password1')
                password2 = request.data.get('password2')
                if password1 == password2 and password1 and password2:
                    User.objects.password_change(user.phone, password1)
                    self.status_bool = True
                    self.detail = 'Пароль изменено переходите на логин'
                else:
                    self.status_bool = False
                    self.detail = 'Пароли не совпадают или данные заполнены некорректно!'
            else:
                self.status_bool = False
                self.detail = 'Неверный пароль!'
        if request.version == 'v2':
            if not self.status_bool:
                self.status_code = status.HTTP_400_BAD_REQUEST
            return api2_response(self)
        return Response({
            'status': self.status_bool,
            'detail': self.detail
        })


class UserInfo(APIView):
    status_code = status.HTTP_200_OK
    detail = 'Все изменении обновлены'
    data = {}
    safe = True

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            serializer = UserInfoSerializer(request.user)
            if request.version == 'v2':
                self.detail = "Информация о пользователе"
                self.data = serializer.data
                self.safe = False
                return api2_response(self)

            return JsonResponse(serializer.data, safe=False)
        else:
            if request.version == 'v2':
                self.detail = "Войдите или зарегистрируйтесь"
                self.status_code = status.HTTP_401_UNAUTHORIZED
                return api2_response(self)
            return Response({"status": False, "detail": "User not found"})


class UserGeoView(APIView):
    status_code = status.HTTP_200_OK
    detail = "Город пользователя"
    data = {
    }
    safe = True

    def get(self, request):
        # reader = geoip2.database.Reader('users/GeoLite2-City.mmdb')
        reader = geoip2.database.Reader('/var/www/api/django/kupizalog/users/GeoLite2-City.mmdb')
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        try:
            response = reader.city(ip)
            city = response.city.name
        except:
            city = "Almaty"

        if request.version == 'v2':
            self.data = {
                'сity': city,
                'ip': ip
            }
            return api2_response(self)

        return Response({
            'City': city,
            'ip': ip,
            "API": request.version,
        })
