from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.utils.translation import gettext as _


class CustomAccessMixin(AccessMixin):
    def handle_permissions(self, request):
        return None

    def dispatch(self, request, *args, **kwargs):
        return self.handle_permissions(request) or super().dispatch(request, *args, **kwargs)


class EmailNotVerifiedMixin(CustomAccessMixin):
    def handle_permissions(self, request):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.email_verified:
            messages.warning(request, _("Your email has already been verified"))
            return redirect('home')
        return super().handle_permissions(request)


class LoginRequiredMixin(CustomAccessMixin):
    def handle_permissions(self, request):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.email_verified:
            return redirect('needs_verification')
        return super().handle_permissions(request)


class IsOrganizerMixin(LoginRequiredMixin):
    def handle_permissions(self, request):
        response = super().handle_permissions(request)
        if response is None and not request.user.is_organizer:
            return self.handle_no_permission()
        return response
