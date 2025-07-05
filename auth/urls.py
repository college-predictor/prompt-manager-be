import auth.views as views
from django.urls import path

urlpatterns = [
    path("login", views.login_api),
    path("logout", views.logout_api),
]