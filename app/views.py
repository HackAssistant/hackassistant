from django.shortcuts import redirect
from django.views import View

from user.mixins import LoginRequiredMixin


class BaseView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.is_organizer():
            return redirect('application_review')
        return redirect('apply_home')


class PrivacyCookies(View):
    def get(self, request, *args, **kwargs):
        return redirect('https://legal.hackersatupc.org/hackupc/privacy_and_cookies')


class LegalNotice(View):
    def get(self, request, *args, **kwargs):
        return redirect('https://legal.hackersatupc.org/hackupc/legal_notice')


class TermsConditions(View):
    def get(self, request, *args, **kwargs):
        return redirect('https://legal.hackersatupc.org/hackupc/terms_and_conditions')
