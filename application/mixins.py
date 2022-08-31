from app.mixins import PermissionRequiredMixin
from application.models import ApplicationTypeConfig


class ApplicationPermissionRequiredMixin(PermissionRequiredMixin):
    def has_permission(self):
        perms = self.get_permission_required()
        application_type = self.get_application_type()
        type_perms = self.get_type_permissions(perms, application_type)
        return self.request.user.has_perms(perms) or (application_type is not None and
                                                      self.request.user.has_perms(type_perms))

    def get_application_type(self):
        if not hasattr(super(), 'get_application_type'):
            return None
        return super().get_application_type()

    def get_type_permissions(self, permissions, application_type):
        result = []
        if application_type is None:
            return result
        for permission in permissions:
            result.append(permission + '_' + application_type.lower())
        return result


class AnyApplicationPermissionRequiredMixin(ApplicationPermissionRequiredMixin):
    def has_permission(self):
        perms = self.get_permission_required()
        if self.request.user.has_perms(perms):
            return True
        for application_type in ApplicationTypeConfig.objects.all().values_list('name', flat=True):
            perms_type = self.get_type_permissions(perms, application_type)
            if self.request.user.has_perms(perms_type):
                return True
        return False
