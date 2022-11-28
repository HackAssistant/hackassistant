from django.contrib import messages
from django.db import Error, transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from app.mixins import TabsViewMixin
from application.mixins import ApplicationPermissionRequiredMixin
from application.models import Application, Edition, ApplicationTypeConfig, ApplicationLog
from friends.filters import FriendsInviteTableFilter
from friends.forms import FriendsForm
from friends.models import FriendsCode
from friends.tables import FriendInviteTable
from review.emails import send_invitation_email
from review.views import ReviewApplicationTabsMixin, ApplicationListInvite
from user.mixins import LoginRequiredMixin, IsOrganizerMixin
from django.utils.translation import gettext_lazy as _


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


class FriendsListInvite(ApplicationPermissionRequiredMixin, IsOrganizerMixin, ReviewApplicationTabsMixin,
                        SingleTableMixin, FilterView):
    template_name = 'invite_friends.html'
    table_class = FriendInviteTable
    permission_required = 'application.can_invite_application'
    table_pagination = {'per_page': 50}
    filterset_class = FriendsInviteTableFilter

    def get_application_type(self):
        return self.request.GET.get('type', 'hacker')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application_type = get_object_or_404(ApplicationTypeConfig, name__iexact=self.get_application_type())
        context.update({'invite': True, 'application_type': application_type, 'Application': Application,
                        'application_stats': ApplicationListInvite.get_application_status(application_type)})
        return context

    def get_queryset(self):
        edition = Edition.get_default_edition()
        application_type = get_object_or_404(ApplicationTypeConfig, name__iexact=self.get_application_type())
        return self.table_class.get_queryset(application_type.application_set.filter(edition_id=edition,
                                                                                     user__friendscode__isnull=False))

    def post(self, request, *args, **kwargs):
        selection = request.POST.getlist('select')
        error = 0
        invited = 0
        for application in Application.objects.actual().filter(user__friendscode__code__in=selection,
                                                               status=Application.STATUS_PENDING):
            log = ApplicationLog(application=application, user=request.user, name='Invited by friends')
            log.changes = {'status': {'old': application.status, 'new': Application.STATUS_INVITED}}
            application.set_status(Application.STATUS_INVITED)
            try:
                with transaction.atomic():
                    application.save()
                    log.save()
                    send_invitation_email(request, application)
                    invited += 1
            except Error:
                error += 1
        if error > 0:
            messages.error(request, _('Invited %s, Error: %s') % (invited, error))
        else:
            messages.success(request, _('Invited: %s' % invited))
        return redirect(reverse('invite_friends') + ('?type=%s' % self.request.GET.get('type', 'hacker')))
