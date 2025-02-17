from django.utils.translation import gettext_lazy as _
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from apps.users.models import User
from django.contrib import admin

# Register your models here.

class UserAdmin(ModelAdmin):
    model = User
    menu_label = _('Users')
    menu_icon = 'user'
    list_display = ('email', 'full_name', 'profile_picture')
    search_fields = ('email', 'full_name')


modeladmin_register(UserAdmin)
admin.site.register(User)
