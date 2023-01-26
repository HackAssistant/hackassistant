# PermissionRequiredMixin [+](/app/mixins.py)

This Mixin is mean to inherit any type of View class and expands the base [Django PermissionRequiredMixin](https://docs.djangoproject.com/en/4.1/topics/auth/default/#the-permissionrequiredmixin-mixin) class.
The new functionality is that you can put a dictionary on the `permission_required` in order to change the permissions between the HTTP method: GET, POST, etc.

## Example

```python
from django.views.generic import View

from app.mixins import PermissionRequiredMixin


class SomeView(PermissionRequiredMixin, View):
    permission_required = {
        'GET': 'app.some_permission',
        'POST': 'app.some_other_permission'
    }
```
