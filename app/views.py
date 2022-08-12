from django.shortcuts import redirect
from django.views import View

from user.mixins import LoginRequiredMixin


class BaseView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.is_organizer():
            return redirect('application_review')
        return redirect('apply_home')
