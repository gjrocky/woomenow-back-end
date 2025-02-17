from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from apps.users.models import User


class MySocialAccount(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        try:
            existing_user = User.objects.get(email=sociallogin.user.email)
            sociallogin.connect(request, existing_user)
        except User.DoesNotExist:
            pass
