from allauth.account.utils import perform_login
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user
        user.email_verified = True
        if not user.id:
            user_class = get_user_model()
            try:
                user = user_class.objects.get(email=user.email)
                sociallogin.state['process'] = 'connect'
                perform_login(request, user, 'none')
            except user_class.DoesNotExist:
                pass
