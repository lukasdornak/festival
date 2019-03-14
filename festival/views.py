from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, TemplateView
from django.shortcuts import redirect, reverse
from django.utils.decorators import method_decorator

from . import models


@method_decorator(login_required, name='dispatch')
class HomeTemplateView(TemplateView):
    template_name = 'festival/home.html'

    def get(self, request, *args, **kwargs):
        role = request.session.get('FESTIVAL_ROLE', None)
        if role:
            return redirect(reverse(role))
        self.first_time = True
        self.nav = bool(request.GET.get('nav', 0))
        self.all_sections = models.Section.objects.all()
        return super().get(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
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
        self.role = kwargs.get('role', None)
        if self.role:
            request.session['FESTIVAL_ROLE'] = self.role
        self.first_time = bool(request.GET.get('first', 0))
        self.nav = bool(request.GET.get('nav', 0))
        self.home = bool(request.GET.get('home', 0))
        return super().get(request, *args, **kwargs)