import os

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls.base import reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from markdown import markdown

from projects.forms import ProjectForm
from projects.models import Project


class AssignmentView(TemplateView):
    template_name = 'projects/assignment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with open(os.path.join(settings.BASE_DIR, 'README.md'), encoding='utf-8') as f:
            assignment_content = f.read()

        context.update({
            'assignment_content': mark_safe(markdown(assignment_content))
        })

        return context


class DashboardView(LoginRequiredMixin, ListView):
    model = Project
    ordering = ('-start_date',)
    context_object_name = 'projects'
    template_name = 'projects/dashboard.html'

    def get_queryset(self):
        projects = super().get_queryset()
        projects = projects.select_related('company')

        return projects


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    success_url = reverse_lazy('dashboard')
