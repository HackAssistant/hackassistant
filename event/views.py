import string
from random import choice

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from django.utils.translation import gettext_lazy as _

from application.mixins import AnyApplicationPermissionRequiredMixin
from application.models import Application, ApplicationLog, Edition
from event.filters import CheckinTableFilter
from event.tables import CheckinTable


class CheckinList(AnyApplicationPermissionRequiredMixin, SingleTableMixin, FilterView):
    permission_required = 'event.can_checkin'
    template_name = 'checkin_list.html'
    table_class = CheckinTable
    filterset_class = CheckinTableFilter

    def get_queryset(self):
        return get_user_model().objects.filter(Q(application__status=Application.STATUS_CONFIRMED,
                                                 application__edition=Edition.get_default_edition()) |
                                               Q(groups__name='Organizer', qr_code='')).distinct()


class CheckinUser(TemplateView):
    template_name = 'checkin_user.html'

    def has_permission(self, types):
        permission = 'event.can_checkin'
        if self.request.user.has_perm(permission):
            return True
        for application_type in types:
            if not self.request.user.has_perm('%s_%s' % (permission, application_type.lower())):
                return False
        return True

    def get_accepted_status_to_checkin(self):
        accepted_status = [Application.STATUS_CONFIRMED]
        if self.request.user.is_staff:
            accepted_status.append(Application.STATUS_ATTENDED)
        return accepted_status

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        User = get_user_model()
        try:
            uid = User.decode_encoded_pk(kwargs.get('uid'))
            user = User.objects.get(pk=uid)
            accepted_status = self.get_accepted_status_to_checkin()
            application_types = list(user.application_set.actual().filter(status__in=accepted_status)
                                     .values_list('type__name', flat=True))
            if user.is_organizer():
                application_types.append('Organizer')
            context.update({'app_user': user, 'types': application_types,
                            'has_permission': self.has_permission(types=application_types)})
        except (User.DoesNotExist, ValueError):
            pass
        return context

    def get_code(self):
        qr_code = self.request.POST.get('qr_code', None)
        if qr_code == '':
            return ''.join([choice(string.ascii_letters + string.digits + string.punctuation) for i in range(12)])
        return qr_code

    def manage_application_confirm(self, application):
        application.set_status(Application.STATUS_ATTENDED)
        application.save()
        application_log = ApplicationLog(application=application, user=self.request.user, comment='',
                                         name='Checked-in')
        application_log.changes = {'status': {'new': Application.STATUS_ATTENDED,
                                              'old': Application.STATUS_CONFIRMED}}
        application_log.save()

    def manage_application_attended(self, application):
        application_log = ApplicationLog(application=application, user=self.request.user, comment='',
                                         name='Changed QR code')
        application_log.save()

    def redirect_successful(self):
        next_ = self.request.GET.get('next', reverse('checkin_list'))
        if next_[0] != '/':
            next_ = reverse('checkin_list')
        return redirect(next_)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        qr_code = self.get_code()
        if context['has_permission'] and len(context['types']) > 0 and qr_code is not None:
            user = context['app_user']
            user.qr_code = qr_code
            accepted_status = self.get_accepted_status_to_checkin()
            applications = user.application_set.actual().filter(status__in=accepted_status)\
                .select_related('type')
            groups = Group.objects.filter(name__in=context['types'])
            with transaction.atomic():
                user.save()
                user.groups.add(*groups)
                for application in applications:
                    if application.status == Application.STATUS_CONFIRMED:
                        self.manage_application_confirm(application)
                    else:
                        self.manage_application_attended(application)
            messages.success(request, _('User checked in!'))
            return self.redirect_successful()
        messages.error(request, _('Permission denied'))
        return self.render_to_response(context)


class CheckinAdminList(CheckinList):
    def get_queryset(self):
        if self.request.user.is_staff:
            return get_user_model().objects.filter(Q(application__status__in=[Application.STATUS_CONFIRMED,
                                                                              Application.STATUS_ATTENDED],
                                                     application__edition=Edition.get_default_edition()) |
                                                   Q(groups__name='Organizer')).distinct()
        return get_user_model().objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'admin': True})
        return context
