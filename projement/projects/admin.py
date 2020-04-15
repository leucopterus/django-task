from django.contrib import admin

from projects.models import Company, Project, ProjectChanges, Tag, ProjectTagRelation


class ProjectTagRelationInline(admin.TabularInline):
    model = ProjectTagRelation
    readonly_fields = ['attached_date']
    extra = 1


class ProjectAdmin(admin.ModelAdmin):
    inlines = (ProjectTagRelationInline,)
    list_display = ('title', 'company', 'start_date', 'end_date')
    list_filter = ('company_id',)
    ordering = ('-start_date',)

    fieldsets = (
        (None, {'fields': ['company', 'title', 'start_date', 'end_date']}),
        ('Estimated hours', {'fields': ['estimated_design', 'estimated_development', 'estimated_testing']}),
        ('Actual hours', {'fields': ['actual_design', 'actual_development', 'actual_testing']}),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ()

        return 'company',


class ProjectTagRelationAdmin(admin.ModelAdmin):
    fields = ['project', 'tag', 'attached_date']
    readonly_fields = ['attached_date']


admin.site.register(Company)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectChanges)
admin.site.register(Tag)
admin.site.register(ProjectTagRelation, ProjectTagRelationAdmin)
