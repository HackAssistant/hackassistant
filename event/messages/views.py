from django.db.models import Case, When
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from app.mixins import PermissionRequiredMixin
from event.messages.filters import AnnouncementTableFilter
from event.messages.forms import AnnouncementForm
from event.messages.models import Announcement
from event.messages.tables import AnnouncementTable


class AnnouncementList(PermissionRequiredMixin, SingleTableMixin, FilterView):
    permission_required = 'event_messages.view_announcement'
    template_name = 'announcement_list.html'
    table_class = AnnouncementTable
    filterset_class = AnnouncementTableFilter
    queryset = Announcement.objects.all().annotate(pending=Case(When(status=Announcement.STATUS_PENDING, then=1),
                                                                default=0)).order_by('-pending', 'datetime')

    def get_permission_required(self):
        if self.request.method == 'POST':
            return ['event_messages.change_announcement']
        return super().get_permission_required()

    def post(self, request, **kwargs):
        announcement = get_object_or_404(Announcement, id=request.POST.get('send'))
        announcement.status = announcement.STATUS_SENT
        announcement.save()
        return redirect(reverse('announcement_list'))


class AnnouncementFormView(PermissionRequiredMixin, TemplateView):
    template_name = 'announcement_form.html'
    permission_required = 'event_messages.add_announcement'

    def get_permission_required(self):
        ann_id = self.kwargs.get('aid', None)
        if ann_id is not None:
            return ['event_messages.change_announcement']
        return super().get_permission_required()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ann_id = self.kwargs.get('aid', None)
        form_kwargs = {}
        if ann_id is not None:
            form_kwargs['instance'] = get_object_or_404(Announcement, id=ann_id)
        else:
            form_kwargs['initial'] = {'datetime': timezone.now()}
        context.update({'form': AnnouncementForm(**form_kwargs), 'announcement': form_kwargs.get('instance', None)})
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        form_kwargs = {}
        announcement = context.get('announcement', None)
        if announcement is not None:
            form_kwargs['instance'] = announcement
        form = AnnouncementForm(request.POST, **form_kwargs)
        if form.is_valid():
            form.save()
            return redirect(reverse('announcement_list'))
        context.update({'form': form})
        return self.render_to_response(context)
