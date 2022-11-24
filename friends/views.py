from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView

from app.mixins import TabsViewMixin
from application.models import Application, Edition
from friends.forms import FriendsForm
from friends.models import FriendsCode
from user.mixins import LoginRequiredMixin


class JoinFriendsView(LoginRequiredMixin, TabsViewMixin, TemplateView):
    template_name = "join_friends.html"

    def handle_permissions(self, request):
        permission = super().handle_permissions(request)
        edition = Edition.get_default_edition()
        if permission is None and not \
                Application.objects.filter(type__name="Hacker", user=request.user, edition=edition).exists():
            return self.handle_no_permission()
        return permission

    def get_current_tabs(self, **kwargs):
        return [("Applications", reverse("apply_home")), ("Friends", reverse("join_friends"))]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            friends_code = FriendsCode.objects.get(user=self.request.user)
            context.update({"friends_code": friends_code})
        except FriendsCode.DoesNotExist:
            context.update({"friends_form": FriendsForm()})
        return context

    def post(self, request, **kwargs):
        action = request.POST.get("action")
        if action not in ["create", "join", "leave"]:
            return HttpResponseBadRequest()
        method = getattr(self, action)
        return method()

    def create(self, **kwargs):
        default = {"user": self.request.user}
        code = kwargs.get("code", None)
        if code is not None:
            default["code"] = code
        FriendsCode(**default).save()
        return redirect(reverse("join_friends"))

    def join(self, **kwargs):
        form = FriendsForm(self.request.POST)
        if form.is_valid():
            code = form.cleaned_data.get("friends_code", None)
            if code is not None and FriendsCode.objects.filter(code=code).exists():
                return self.create(code=code)
            form.add_error("friends_code", "Invalid code!")
        context = self.get_context_data()
        context.update({"friends_form": form})
        return self.render_to_response(context)

    def leave(self, **kwargs):
        try:
            friends_code = FriendsCode.objects.get(user=self.request.user)
            friends_code.delete()
        except FriendsCode.DoesNotExist:
            pass
        return redirect(reverse("join_friends"))
