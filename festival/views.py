from django.views.generic import ListView, TemplateView
from django.shortcuts import redirect, reverse

from . import models


class HomeTemplateView(TemplateView):
    template_name = 'festival/home.html'

    def get(self, request, *args, **kwargs):
        role = request.session.get('FESTIVAL_ROLE', None)
        if role:
            return redirect(reverse(role))
        self.first_time = True
        self.all_sections = models.Section.objects.all()
        return super().get(request, *args, **kwargs)


class SectionListView(ListView):
    model = models.Section

    def get_queryset(self):
        self.all_sections = super().get_queryset()
        return self.all_sections.filter(role=self.role)

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        for obj in self.object_list:
            if obj.widget:
                obj.widget_context = obj.get_widget().get_context_data(self)
        return context_data

    def get(self, request, *args, **kwargs):
        self.first_time = not bool(request.session.get('FESTIVAL_ROLE', None))
        self.role = kwargs.get('role', None)
        if self.role:
            request.session['FESTIVAL_ROLE'] = self.role
        return super().get(request, *args, **kwargs)