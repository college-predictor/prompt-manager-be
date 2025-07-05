from auth.backend import BackendType, GoogleAuthBackend
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
import django.contrib.auth

from auth.models import User

@require_POST
def login_api(request):
    auth_type = BackendType.from_val(int(request.POST.get("auth_type")))

    if auth_type == BackendType.GOOGLE:
        backend = GoogleAuthBackend({'SA_KEY_FILE': settings.FIREBASE_SA_FILE})
        user_details = backend.verify_token(request.POST.get("token"))

        user = User.objects.filter(email=user_details['email'])
        if not user.exists():
            user = User.objects.create_user(email=user_details['email'], name=user_details['name'])
        
        django.contrib.auth.login(request, user)
        return JsonResponse({"result": "ok", "data": {"email": user.email, "name": user.name}})
    
    return JsonResponse({"result": "failure", "data": {"message": "invalid auth backend"}})

@require_POST
def logout_api(request):
    django.contrib.auth.logout(request)
    return JsonResponse({"result": "ok"})