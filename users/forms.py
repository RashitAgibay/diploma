from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User


class LoginForm(forms.Form):
    phone = forms.IntegerField(label="Your phone number")
    password = forms.CharField(widget=forms.PasswordInput)


class VerifyForm(forms.Form):
    key = forms.IntegerField(label="Enter Your OTP here")


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phone',)

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        gs = User.objects.filter(phone=phone)
        if gs.exists():
            raise forms.ValidationError("phone is token")
        return phone

    def clean_password(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password1")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("password don't mach")
        return password2


class UserAdminCreationForm(forms.ModelForm):

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phone',)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password1")

        if password1 and password2 and password1!=password2:
            raise forms.ValidationError("password don't mach")
        return password2

    def save(self, commit=True):

        user = super(UserAdminCreationForm,self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):

    # password = ReadOnlyPasswordHashField() todo delete this comment just read only

    class Meta:
        model = User
        fields = ('phone', 'password', 'first_name', 'last_name', 'active', 'admin')

    def clean_password(self):

        return self.initial['password']

