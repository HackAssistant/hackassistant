from django.shortcuts import redirect
from django.views.generic import TemplateView


class BaseView(TemplateView):
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_organizer():
            return redirect('apply_home')
        elif request.user.is_authenticated:
            return redirect('apply_home')
        return super().get(request, *args, **kwargs)
