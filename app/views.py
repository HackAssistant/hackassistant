from django.shortcuts import redirect, render
from django.views import View
from django_tex.shortcuts import render_to_pdf

from app.template import app_variables
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


def handler_error_404(request, exception=None, **kwargs):
    return render(request=request, template_name='errors/404.html', context={'exception': exception}, status=404)


def handler_error_500(request, exception=None, **kwargs):
    return render(request=request, template_name='errors/500.html', context={'exception': exception}, status=500)


def handler_error_403(request, exception=None, **kwargs):
    return render(request=request, template_name='errors/403.html', context={'exception': exception}, status=403)


def handler_error_400(request, exception=None, **kwargs):
    return render(request=request, template_name='errors/400.html', context={'exception': exception}, status=400)


class LatexTemplateView(View):
    template_name = ''
    file_name = ''

    def get_context_data(self, **kwargs):
        return app_variables(self.request)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render_to_pdf(request, self.template_name, context, filename=self.file_name)
