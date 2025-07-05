from django.urls import path, include

urlpatterns = [
    path("auth/", include('authen.urls')),
    path("api/", include('api.urls')),
]
