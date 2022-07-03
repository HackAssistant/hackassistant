from django.urls import reverse
from django.views.generic import TemplateView


class BaseView(TemplateView):
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'tabs': [('Aaaaaaa', reverse('home'), True),('Bbbbbbbb1', '/b', False), ('Bbbbbbbb2', '/b', False), ('Bbbbbbbb3', '/b', False) ,('Bbbbbbbb4', '/b', False) ,('Bbbbbbbb5', '/b', False) ,('Bbbbbbbb6', '/b', False),('Bbbbbbbb7', '/b', False),('Bbbbbbbb8', '/b', False),('Here', '/a', False),('Bbbbbbbb', '/a', False)]})
        return context
