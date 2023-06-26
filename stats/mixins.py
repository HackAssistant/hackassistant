from app.mixins import PermissionRequiredMixin


class StatsPermissionRequiredMixin(PermissionRequiredMixin):
    def has_permission(self, application_type=None):
        if not self.request.user.is_organizer:
            return False
        perms = self.get_permission_required()
        model_name = self.kwargs.get('model', '').lower()
        model_perms = ['%s_%s' % (perm, model_name) for perm in perms]
        return self.request.user.has_perms(perms) or self.request.user.has_perms(model_perms)
