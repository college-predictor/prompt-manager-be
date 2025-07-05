import api.views as views
from django.urls import path

urlpatterns = [
    path("config", views.config_api),
    path("projects", views.projects_api),
    path("projects/<int:project_id>", views.one_project_api),
]