from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView

from friends.forms import FriendsForm
from friends.models import FriendsCode


class JoinFriendsView(TemplateView):
    template_name = "join_friends.html"

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
        if action not in ["create", "join"]:
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
