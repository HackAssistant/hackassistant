import copy
import logging
from abc import abstractmethod

from app.mixins import PermissionRequiredMixin


class AbstractTableMixin:
    def __init__(self, *args, **kwargs):
        force_update = kwargs.pop('force_update')
        queryset = self.get_queryset(force_update=force_update)
        if 'filter_class' in kwargs:
            filter_class = kwargs.pop('filter_class')
            request_get = kwargs.pop('request_get')
            filterset = filter_class(request_get, queryset=queryset)
            self.filterset = filterset
            kwargs['data'] = filterset.qs
        else:
            kwargs['data'] = queryset
        super().__init__(*args, **kwargs)

    @abstractmethod
    def get_queryset(self):
        pass


class TablesFiltersMixin:
    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        model = self._meta.model

        self.is_bound = data is not None
        self.data = data or {}
        self.queryset = queryset
        self.request = request
        self.form_prefix = prefix

        self.filters = copy.deepcopy(self.base_filters)

        # propagate the model and filterset to the filters
        for filter_ in self.filters.values():
            filter_.model = model
            filter_.parent = self

    #  Modify filter to filter with python method as queryset is a python list.
    def filter_queryset(self, queryset):
        for name, value in self.form.cleaned_data.items():
            #  Filter methods must return True/False if item must be on list or not
            #  def filter_field_name(self, instance, form_value)
            filter_method = getattr(self, 'filter_' + name, None)
            if filter_method is None:
                logger = logging.getLogger(__name__)
                logger.info('Filter %s skipped: No filter method found')
            else:
                queryset = filter(lambda item: filter_method(item, value), queryset)
        return queryset

    @property
    def qs(self):
        if not hasattr(self, "_qs"):
            qs = self.queryset
            if self.is_bound:
                # ensure form validation before filtering
                self.errors
                qs = self.filter_queryset(qs)
            self._qs = qs
        return self._qs


class TablePermissionRequiredMixin(PermissionRequiredMixin):
    def has_permission(self, application_type=None):
        if not self.request.user.is_organizer:
            return False
        perms = self.get_permission_required()
        model_name = self.kwargs.get('model', '').lower()
        model_perms = ['%s_%s' % (perm, model_name) for perm in perms]
        return self.request.user.has_perms(perms) or self.request.user.has_perms(model_perms)
