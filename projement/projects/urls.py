from django.conf.urls import url
from django.urls import path

from projects.views import (
    AssignmentView,
    DashboardView,
    ProjectUpdateView,
    ProjectTagView,
    TagListView,
    TagCreateView,
    TagRetrieveView,
    TagUpdateView,
    TagDeleteView,
)


urlpatterns = [
    url(r'^$', AssignmentView.as_view(), name='assignment'),
    url(r'^dashboard/$', DashboardView.as_view(), name='dashboard'),
    url(r'^dashboard/(?P<file>[-\w]*)/$', DashboardView.as_view(), name='dashboard'),
    url(r'^projects/(?P<pk>[0-9]+)-(?P<slug>[-\w]*)/$', ProjectUpdateView.as_view(), name='project-update'),
    url(r'^projects/(?P<pk>[0-9]+)-(?P<slug>[-\w]*)/tags/$', ProjectTagView.as_view(), name='project-tag-management'),
    path('tags/', TagListView.as_view(), name='tags-list'),
    path('tags/add/', TagCreateView.as_view(), name='tag-create'),
    path('tags/<int:pk>/', TagRetrieveView.as_view(), name='tag-retrieve'),
    path('tags/<int:pk>/update/', TagUpdateView.as_view(), name='tag-update'),
    path('tags/<int:pk>/delete/', TagDeleteView.as_view(), name='tag-delete'),
]
