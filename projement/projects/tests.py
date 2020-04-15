from decimal import Decimal
from copy import deepcopy

from django.contrib.auth.models import User
from django.db.models import F
from django.test import Client, TestCase
from django.utils.text import slugify

from projects.models import (
    Company,
    Project,
    ProjectChanges,
    Tag,
    ProjectTagRelation,
)


class DashboardTestCase(TestCase):

    fixtures = ['projects/fixtures/initial.json']

    def setUp(self):
        super().setUp()

        username, password = 'Thorgate', 'thorgate123'
        User.objects.create_user(username=username, email='info@throgate.eu', password=password)

        self.authenticated_client = Client()
        self.authenticated_client.login(username=username, password=password)

        self.projects_from_db = Project.objects.all().order_by(F('end_date').desc(nulls_first=True))

    def test_dashboard_requires_authentication(self):

        # Anonymous users can't see the dashboard

        client = Client()
        response = client.get('/dashboard/')
        self.assertRedirects(response, '/login/?next=/dashboard/')

        # Authenticated users can see the dashboard

        response = self.authenticated_client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)

    def test_projects_on_dashboard(self):

        # There are 3 projects on the dashboard (loaded from the fixtures)

        response = self.authenticated_client.get('/dashboard/')
        projects = response.context['projects']
        self.assertEqual(projects.count(), self.projects_from_db.count())

        self.assertListEqual(list(projects), list(self.projects_from_db))

    def test_project_from_dashboard_to_excel_download(self):

        response = self.authenticated_client.get('/dashboard/excel-file/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.get('PATH_INFO'), '/dashboard/excel-file/')


class ProjectsTestCase(TestCase):
    fixtures = ['projects/fixtures/initial.json']

    def setUp(self):
        super().setUp()

        self.username, password = 'Thorgate', 'thorgate123'
        User.objects.create_user(username=self.username, email='info@throgate.eu', password=password)

        self.authenticated_client = Client()
        self.authenticated_client.login(username=self.username, password=password)

        self.projects = Project.objects.order_by('id')
        self.project_changes = ProjectChanges.objects.count()

        self.data_without_changes = {'actual_design': '0',
                                     'actual_development': '0',
                                     'actual_testing': '0'}
        self.data_with_changes = {'actual_design': '1',
                                  'actual_development': '2',
                                  'actual_testing': '3'}

    def test_project_has_ended(self):

        # 2 of the projects have ended
        self.assertListEqual([p.has_ended for p in self.projects], [True, True, False])

    def test_project_is_over_budget(self):

        # 1 of the projects is over budget
        self.assertListEqual([p.is_over_budget for p in self.projects], [True, False, False])

    def test_total_estimated_hours(self):

        self.assertListEqual([p.total_estimated_hours for p in self.projects], [690, 170, 40])

    def test_total_actual_hours(self):

        self.assertListEqual([p.total_actual_hours for p in self.projects], [739, 60, 5])

    def test_add_actual_time_without_changes(self):

        project = initial = self.projects.last()
        initial_changes = self.project_changes
        response = self.authenticated_client.post(f'{project.get_absolute_url()}',
                                                  data=self.data_without_changes)
        self.assertEqual(response.status_code, 302)
        project.refresh_from_db()
        changes = ProjectChanges.objects.count()

        self.assertEqual(project.actual_design, initial.actual_design + Decimal(self.data_without_changes['actual_design']))
        self.assertEqual(project.actual_development, initial.actual_development + Decimal(self.data_without_changes['actual_development']))
        self.assertEqual(project.actual_testing, initial.actual_testing + Decimal(self.data_without_changes['actual_testing']))

        self.assertEqual(initial_changes, changes)

    def test_add_actual_time_with_changes(self):

        project = self.projects.last()
        initial = deepcopy(project)
        initial_changes = self.project_changes
        response = self.authenticated_client.post(f'{project.get_absolute_url()}',
                                                  data=self.data_with_changes)
        self.assertEqual(response.status_code, 302)
        project.refresh_from_db()
        changes = ProjectChanges.objects.all()
        last_change = changes.last()

        self.assertEqual(project.actual_design, initial.actual_design + Decimal(self.data_with_changes['actual_design']))
        self.assertEqual(project.actual_development, initial.actual_development + Decimal(self.data_with_changes['actual_development']))
        self.assertEqual(project.actual_testing, initial.actual_testing + Decimal(self.data_with_changes['actual_testing']))

        self.assertEqual(changes.count() - initial_changes, 1)

        self.assertEqual(last_change.user.username, self.username)

        self.assertEqual(last_change.initial_actual_design, initial.actual_design)
        self.assertEqual(last_change.delta_actual_design, Decimal(self.data_with_changes['actual_design']))
        self.assertEqual(last_change.result_actual_design, project.actual_design)

        self.assertEqual(last_change.initial_actual_development, initial.actual_development)
        self.assertEqual(last_change.delta_actual_development, Decimal(self.data_with_changes['actual_development']))
        self.assertEqual(last_change.result_actual_development, project.actual_development)

        self.assertEqual(last_change.initial_actual_testing, initial.actual_testing)
        self.assertEqual(last_change.delta_actual_testing, Decimal(self.data_with_changes['actual_testing']))
        self.assertEqual(last_change.result_actual_testing, project.actual_testing)


class TagsTestCase(TestCase):
    fixtures = ['projects/fixtures/initial.json']

    def setUp(self):
        super().setUp()

        username, password = 'Thorgate', 'thorgate123'
        User.objects.create_user(username=username, email='info@throgate.eu', password=password)

        self.authenticated_client = Client()
        self.authenticated_client.login(username=username, password=password)

        self.tags = Tag.objects.all()
        self.selected_tag = self.tags.last()
        self.new_tag_data = {'name': 'devops'}

        self.tag_list_url = '/tags/'
        self.tag_create_url = '/tags/add/'
        self.tag_retrieve_url = f'/tags/{self.selected_tag.id}/'
        self.tag_update_url = f'/tags/{self.selected_tag.id}/update/'
        self.tag_delete_url = f'/tags/{self.selected_tag.id}/delete/'

        self.selected_project = Project.objects.exclude(tags__in=(self.selected_tag,)).first()
        self.project_add_tag_url = f'/projects/{self.selected_project.id}-{slugify(self.selected_project.title)}/tags/'
        self.project_add_tag_data = {'tags': [self.selected_tag.id,]}

    def test_create_tag(self):
        initial_tags_amount = self.tags.count()
        response = self.authenticated_client.post(self.tag_create_url, data=self.new_tag_data)
        new_tag_obj = Tag.objects.last()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.tags.count() - initial_tags_amount, 1)
        self.assertEqual(new_tag_obj.name, self.new_tag_data.get('name'))

    def test_list_tags(self):
        response = self.authenticated_client.get(self.tag_list_url)
        all_tags = Tag.objects.all()

        self.assertEqual(response.status_code, 200)
        tags = response.context['tags']
        self.assertListEqual(list(tags), list(all_tags))

    def test_tag_retrieve(self):
        response = self.authenticated_client.get(self.tag_retrieve_url)

        self.assertEqual(response.status_code, 200)
        tag = response.context['tag']
        self.assertEqual(self.selected_tag, tag)

    def test_update_tag(self):
        response = self.authenticated_client.post(self.tag_update_url, data=self.new_tag_data)

        self.assertEqual(response.status_code, 302)
        self.selected_tag.refresh_from_db()
        self.assertEqual(self.selected_tag.name, self.new_tag_data.get('name'))

    def test_delete_tag(self):
        response = self.authenticated_client.delete(self.tag_delete_url)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Tag.objects.filter(id=self.selected_tag.id).exists())

    def test_add_tag_to_project(self):
        response = self.authenticated_client.post(self.project_add_tag_url, self.project_add_tag_data)

        self.assertEqual(response.status_code, 302)
        self.selected_project.refresh_from_db()
        self.assertEqual(self.selected_tag in self.selected_project.tags.all(), True)
