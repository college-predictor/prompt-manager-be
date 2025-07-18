from django.urls import path
from . import views

urlpatterns = [
    path("config", views.config_api),
    path("projects", views.projects_api),
    path("projects/<int:project_id>", views.one_project_api),
    
    # Collection endpoints
    path("projects/<int:project_id>/collections", views.collections_api),
    path("projects/<int:project_id>/collections/<int:collection_id>", views.one_collection_api),
    
    # Prompt endpoints
    path("projects/<int:project_id>/prompts", views.prompts_api),
    path("projects/<int:project_id>/prompts/<int:prompt_id>", views.one_prompt_api),
]