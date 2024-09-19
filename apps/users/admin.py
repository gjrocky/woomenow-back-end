from django.utils.translation import gettext_lazy as _
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from apps.users.models import User


# Register your models here.

class UserAdmin(ModelAdmin):
    model = User
    menu_label = _('Users')
    menu_icon = 'user'  # Icon for the user menu
    list_display = ('email', 'full_name', 'profile_picture')
    search_fields = ('email', 'full_name')


# Register the user model to the wagtail admin interface
modeladmin_register(UserAdmin)
