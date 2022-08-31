from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from django.utils.translation import gettext_lazy as _

from application.mixins import AnyApplicationPermissionRequiredMixin
from application.models import Application, ApplicationLog
from event.filters import CheckinTableFilter
from event.tables import CheckinTable


class CheckinList(AnyApplicationPermissionRequiredMixin, SingleTableMixin, FilterView):
    permission_required = 'can_checkin_application'
    template_name = 'checkin_list.html'
    table_class = CheckinTable
    filterset_class = CheckinTableFilter
    queryset = get_user_model().objects.filter(application__status=Application.STATUS_CONFIRMED).distinct()


class CheckinUser(TemplateView):
    template_name = 'checkin_user.html'

    def has_permission(self, types):
        permission = 'can_checkin_application'
        if self.request.user.has_perm(permission):
            return True
        for application_type in types:
            if not self.request.user.has_perm('%s_%s' % (permission, application_type.lower())):
                return False
        return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        User = get_user_model()
        try:
            uid = User.decode_encoded_pk(kwargs.get('uid'))
            user = User.objects.get(pk=uid)
            application_types = user.application_set.filter(status=Application.STATUS_CONFIRMED)\
                .values_list('type__name', flat=True)
            context.update({'app_user': user, 'types': application_types,
                            'has_permission': self.has_permission(types=application_types)})
        except (User.DoesNotExist, ValueError):
            pass
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        qr_code = request.POST.get('qr_code', '')
        if context['has_permission'] and len(context['types']) > 0 and qr_code != '':
            user = context['app_user']
            user.qr_code = qr_code
            applications = user.application_set.filter(status=Application.STATUS_CONFIRMED).select_related('type')
            groups = Group.objects.filter(name__in=context['types'])
            with transaction.atomic():
                user.save()
                user.groups.add(*groups)
                for application in applications:
                    application.set_status(Application.STATUS_ATTENDED)
                    application.save()
                    application_log = ApplicationLog(application=application, user=request.user, comment='',
                                                     name='Checked-in')
                    application_log.changes = {'status': {'new': Application.STATUS_ATTENDED,
                                                          'old': Application.STATUS_CONFIRMED}}
                    application_log.save()
            return redirect(reverse('checkin_list'))
        messages.error(request, _('Permission denied'))
        return self.render_to_response(context)
