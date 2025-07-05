import json
from authen.backend import BackendType, GoogleAuthBackend
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import django.contrib.auth

from authen.models import User

GOOGLE_BACKEND = GoogleAuthBackend.get_instance()

@require_POST
def login_api(request):
    data = json.loads(request.body.decode('utf-8'))
    auth_type = BackendType.from_val(int(data["auth_type"]))

    if auth_type == BackendType.GOOGLE:
        user_details = GOOGLE_BACKEND.verify_token(data["token"])

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