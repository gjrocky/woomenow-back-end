from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register

from apps.users.models import User


# Register your models here.

class WagtailUserAdmin(ModelAdmin):
    model = User
    menu_label = _('Users')
    menu_icon = 'user'
    list_display = ('email', 'first_name', 'profile_picture')
    search_fields = ('email', 'first_name')


class UserAdmin(admin.ModelAdmin):
    model = User
    menu_label = _('Users')
    menu_icon = 'user'
    list_display = ('email', 'first_name', 'profile_picture')
    search_fields = ('email', 'first_name')


modeladmin_register(WagtailUserAdmin)
admin.site.register(User, UserAdmin)
