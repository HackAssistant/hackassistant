from django.contrib.auth.mixins import PermissionRequiredMixin


class ApplicationPermissionRequiredMixin(PermissionRequiredMixin):
    def has_permission(self):
        perms = self.get_permission_required()
        application_type = self.get_application_type()
        type_perms = self.get_type_permissions(perms, application_type)
        return self.request.user.has_perms(perms) or (application_type is not None and
                                                      self.request.user.has_perms(type_perms))

    def get_permission_required(self):
        permissions = super().get_permission_required()
        if isinstance(permissions, dict):
            permissions = permissions.get(self.request.method, [])
        return permissions

    def get_application_type(self):
        return None

    def get_type_permissions(self, permissions, application_type):
        result = []
        if application_type is None:
            return result
        for permission in permissions:
            result.append(permission + '_' + application_type.lower())
        return result
