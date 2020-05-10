from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.core.validators import RegexValidator
from unique.models import UniqueSys, City, GoalOfSupport
from images.models import Image
import datetime


class UserManager(BaseUserManager):

    use_in_migrations = True

    def create_user(self, phone, password=None, is_staff=False, is_active=True, is_admin=False, first_name=None,
                    last_name=None, email=None):
        unique = UniqueSys.objects.create(object_name='user')  # todo automatic model name getter function or mixin
        unique.save()
        if not phone:
            raise ValueError("Users must have Phone")
        if not password:
            raise ValueError("user must have Password")
        user_obj = self.model(
            phone=phone
        )

        user_obj.staff = is_staff
        user_obj.active = is_active
        user_obj.admin = is_admin
        user_obj.first_name = first_name
        user_obj.last_name = last_name
        user_obj.email = email
        user_obj.unique = unique
        user_obj.set_password(password)
        user_obj.save(using=self._db)
        return user_obj

    def password_change(self, phone, password):
        current_user = User.objects.filter(phone=phone).first()
        current_user.set_password(password)
        # current_user.save(using=self._db)  # todo i don't know why self._db
        return current_user.save()

    def create_staffuser(self, phone, password=None, *args):
        user = self.create_user(
            phone=phone,
            password=password,
            is_staff=True,
            *args,
        )
        return user

    def create_superuser(self, phone, password=None, *args):
        user = self.create_user(
            phone,
            password=password,
            is_staff=True,
            is_admin=True,
            *args,
        )
        return user


class User(AbstractBaseUser):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{10}$',
                                 message="Phone must be entered in the format: last 10 numbers saves in db")
    phone = models.CharField(unique=True, validators=[phone_regex], max_length=11)
    email = models.EmailField(unique=True, null=True)
    unique = models.ForeignKey(UniqueSys, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    patronymic = models.CharField(max_length=50, blank=True, null=True)
    iin = models.CharField(max_length=12, null=True)
    date_of_birth = models.DateField(default=datetime.date.today, null=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, default=None)
    deleted_at = models.DateTimeField(blank=True, null=True)
    first_login = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone

    def get_full_name(self):
        if self.first_name and self.last_name:
            return self.first_name+" "+self.last_name+" | phone : "+self.phone
        else:
            return self.get_short_name()

    def get_short_name(self):
        return self.phone

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active


class PhoneOTP(models.Model):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{10}$',
                                 message="Phone must be entered in the format: last 10 number saves in db")
    phone = models.CharField(unique=True, validators=[phone_regex], max_length=11)
    otp = models.CharField(max_length=9, blank=True, null=True)
    count = models.IntegerField(default=0, help_text="Number of OTP sent")
    validate = models.BooleanField(default=False, help_text="IF OTP verification got successful")
    forgot = models.BooleanField(default=False, help_text="True Only for forgot Password")
    timestamp = models.DateTimeField(auto_now=True)
    resent_count = models.IntegerField(default=0, help_text="Resent count")  # todo

    def __str__(self):
        return self.phone + " sent code -> " + self.otp


class Support(models.Model):
    goal_of_support = models.ForeignKey(GoalOfSupport, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100,  null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title
