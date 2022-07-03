from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.utils.translation import gettext as _


class LoginRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.email_verified:
            return redirect('needs_verification')
        return super().dispatch(request, *args, **kwargs)


class EmailNotVerifiedMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.email_verified:
            messages.warning(request, _("Your email has already been verified"))
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
