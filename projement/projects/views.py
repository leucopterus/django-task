import os

import xlwt
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.http import HttpResponseRedirect, HttpResponse
from django.urls.base import reverse_lazy
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from markdown import markdown


from projects.forms import ProjectForm, TagEditForm, ProjectTagEditForm
from projects.models import Project, ProjectChanges, Tag


class AssignmentView(TemplateView):
    template_name = 'projects/assignment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with open(os.path.join(os.path.dirname(settings.BASE_DIR), 'README.md'), encoding='utf-8') as f:
            assignment_content = f.read()

        context.update({
            'assignment_content': mark_safe(markdown(assignment_content))
        })

        return context


class DashboardView(LoginRequiredMixin, ListView):
    model = Project
    ordering = (F('end_date').desc(nulls_first=True),)
    context_object_name = 'projects'
    template_name = 'projects/dashboard.html'

    def get_queryset(self):
        projects = super().get_queryset()
        projects = projects.select_related('company')
        return projects

    def get(self, request, *args, **kwargs):
        if kwargs.get('file'):
            return self._download_excel_data(request)
        return super().get(request, *args, **kwargs)

    def _download_excel_data(self, request):
        current_time = timezone.now()
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = f'attachment; filename="Dashboard_{current_time}.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet("dashboard")
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        columns = ['Project', 'Company', 'Estimated', 'Actual', 'Tags']
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
        font_style = xlwt.XFStyle()

        data = []
        full_data = self.get_queryset().prefetch_related('tags').order_by(F('end_date').desc(nulls_first=True))
        for data_piece in full_data:
            piece = [data_piece.title, data_piece.company.name, data_piece.total_estimated_hours,
                     data_piece.total_actual_hours, ', '.join(data_piece.tags.values_list('name', flat=True))]
            data.append(piece)

        for data_row in data:
            row_num = row_num + 1
            for col_num in range(len(data_row)):
                ws.write(row_num, col_num, data_row[col_num], font_style)

        wb.save(response)
        return response


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    success_url = reverse_lazy('dashboard')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        obj = self.model.objects.get(pk=kwargs.get('pk'))
        form = self.get_form()
        if form.is_valid():
            self.object = form.save(commit=False)
            self.object.actual_design += obj.actual_design
            self.object.actual_development += obj.actual_development
            self.object.actual_testing += obj.actual_testing
            self.object.save()
            self._change_project_history(request, form, obj)
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)

    def _change_project_history(self, request, form, obj):
        if not any(form.cleaned_data.values()):
            return
        context = {}
        fields = [field.name for field in ProjectChanges._meta.get_fields() if field.name not in ('id', 'change_date')]
        for field in fields:
            data = None
            if field == 'user':
                data = request.user
            elif field == 'project':
                data = self.object
            elif 'initial' in field:
                key = '_'.join(field.split('_')[1:])
                data = obj.__dict__.get(key)
            elif 'delta' in field:
                key = '_'.join(field.split('_')[1:])
                data = form.cleaned_data.get(key)
            elif 'result' in field:
                key = '_'.join(field.split('_')[1:])
                data = self.object.__dict__.get(key)
            if data:
                context.setdefault(field, data)
        new_obj = ProjectChanges.create(**context)
        new_obj.save()


class ProjectTagView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectTagEditForm
    template_name = 'projects/project_tag_edit.html'

    def get_success_url(self):
        return reverse_lazy('dashboard')


class TagListView(LoginRequiredMixin, ListView):
    model = Tag
    context_object_name = 'tags'
    template_name = 'projects/tags.html'

    def get_queryset(self):
        tags = super().get_queryset()
        return tags


class TagRetrieveView(LoginRequiredMixin, DetailView):
    template_name = 'projects/tag_retrieve.html'
    model = Tag
    context_object_name = 'tag'


class TagCreateView(LoginRequiredMixin, CreateView):
    form_class = TagEditForm
    model = Tag
    template_name = 'projects/tag_create_or_update.html'

    def get_success_url(self):
        return reverse_lazy('tags-list')


class TagUpdateView(LoginRequiredMixin, UpdateView):
    model = Tag
    form_class = TagEditForm
    template_name = 'projects/tag_create_or_update.html'

    def get_success_url(self):
        return reverse_lazy('tag-retrieve', kwargs={'pk': self.kwargs.get('pk')})


class TagDeleteView(LoginRequiredMixin, DeleteView):
    # login_url = '/login/'
    model = Tag
    success_url = reverse_lazy('tags-list')
