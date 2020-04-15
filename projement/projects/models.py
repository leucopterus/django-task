from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User


class Company(models.Model):

    class Meta:
        verbose_name_plural = "companies"

    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Project(models.Model):

    company = models.ForeignKey('projects.Company', on_delete=models.PROTECT, related_name='projects')

    title = models.CharField('Project title', max_length=128)
    start_date = models.DateField('Project start date', blank=True, null=True)
    end_date = models.DateField('Project end date', blank=True, null=True)

    estimated_design = models.DecimalField(max_digits=6,
                                           decimal_places=2,
                                           verbose_name='Estimated design hours')
    actual_design = models.DecimalField(max_digits=6,
                                        decimal_places=2,
                                        verbose_name='Actual design hours',
                                        default=0)

    estimated_development = models.DecimalField(max_digits=6,
                                                decimal_places=2,
                                                verbose_name='Estimated development hours')
    actual_development = models.DecimalField(max_digits=6,
                                             decimal_places=2,
                                             verbose_name='Actual development hours',
                                             default=0)

    estimated_testing = models.DecimalField(max_digits=6,
                                            decimal_places=2,
                                            verbose_name='Estimated testing hours')
    actual_testing = models.DecimalField(max_digits=6,
                                         decimal_places=2,
                                         verbose_name='Actual testing hours',
                                         default=0)

    tags = models.ManyToManyField('Tag', through='ProjectTagRelation')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('project-update', kwargs={'pk': self.pk, 'slug': slugify(self.title)})

    @property
    def has_ended(self):
        return self.end_date is not None and self.end_date < timezone.now().date()

    @property
    def total_estimated_hours(self):
        return self.estimated_design + self.estimated_development + self.estimated_testing

    @property
    def total_actual_hours(self):
        return self.actual_design + self.actual_development + self.actual_testing

    @property
    def is_over_budget(self):
        return self.total_actual_hours > self.total_estimated_hours


class ProjectChanges(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    change_date = models.DateTimeField(auto_now_add=True)
    initial_actual_design = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    delta_actual_design = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    result_actual_design = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    initial_actual_development = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    delta_actual_development = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    result_actual_development = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    initial_actual_testing = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    delta_actual_testing = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    result_actual_testing = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = 'Project changes'

    def __str__(self):
        return f'{self.user} added hours to {self.project}'

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=16)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tag-retrieve', kwargs={'pk': self.pk})


class ProjectTagRelation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    attached_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.tag} is attached to a {self.project} project'
