from django.forms.models import ModelForm
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from projects.models import Project, Tag


class ProjectForm(ModelForm):
    actual_design = forms.DecimalField(max_digits=6, decimal_places=2)
    actual_development = forms.DecimalField(max_digits=6, decimal_places=2)
    actual_testing = forms.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        model = Project
        fields = ['actual_design', 'actual_development', 'actual_testing']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'UPDATE'))


class ProjectTagEditForm(ModelForm):
    class Meta:
        model = Project
        fields = ['tags']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'UPDATE'))


class TagEditForm(ModelForm):
    class Meta:
        model = Tag
        fields = ['name']
