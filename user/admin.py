from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group

from user.forms import UserChangeForm, UserCreationForm
from user.models import User, BlockedUser, LoginRequest


class PermissionQuerysetMixin:
    permission_field_name = ''

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == self.permission_field_name:
            qs = kwargs.get("queryset", db_field.remote_field.model.objects)
            # Avoid a major performance hit resolving permission names which
            # triggers a content_type load:
            kwargs["queryset"] = qs.filter(content_type__app_label='application',
                                           content_type__model__in=['application', 'applicationlog'])
        return super().formfield_for_manytomany(db_field, request=request, **kwargs)


class UserAdmin(PermissionQuerysetMixin, BaseUserAdmin):
    permission_field_name = "user_permissions"

    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'is_staff')
    list_filter = ('is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'diet', 'other_diet', 'gender',
                                      'other_gender', 'under_age', 'tshirt_size', 'qr_code')}),
        ('Permissions', {'fields': ('email_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email', 'first_name', 'last_name')
    filter_horizontal = ()


class GroupAdmin(PermissionQuerysetMixin, BaseGroupAdmin):
    permission_field_name = 'permissions'


# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
admin.site.register(LoginRequest)
admin.site.register(BlockedUser)
