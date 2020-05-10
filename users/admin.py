from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.contrib import admin
User = get_user_model()

from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserAdminCreationForm, UserAdminChangeForm
from .models import PhoneOTP, Support
admin.site.register([PhoneOTP, Support])

class UserAdmin(BaseUserAdmin):

    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The field to be used in Displaying the User Mod model
    #
    #
    list_display = ('phone', 'first_name', 'last_name')
    list_filter = ('active', 'staff', 'admin')
    fieldsets = (
        (None, {'fields': ('phone', 'password', 'image')}),
        ('Personal_info', {'fields':('first_name', 'last_name')}),
        ('Permissions', {'fields': ('active', 'admin', 'staff')}),
    )

    add_fieldsets = (
        (None,{
            'classes': ('wide', ),
            'fields': ('phone', 'password1', 'password2')}
        ),
    )

    search_fields = ('phone', 'first_name', 'last_name')
    ordering = ('phone', 'first_name', 'last_name')
    filter_horizontal = ()
    # inlines = (Prof)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)


admin.site.register(User, UserAdmin)
