import json
import api.models as models
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def projects_api(request):
    data = json.loads(request.body.decode('UTF-8'))
    verb = data.get('action', 'list')

    if verb == 'list':
        project_links = models.ProjectMembership.objects.filter(user=request.user)
        project_data = []

        for link in project_links:
            project = link.project
            project_data.append({
                'role': link.role,
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'models': [
                    model.serialize() for model in project.llm_models.all()
                ]
            })

        return JsonResponse({"result": "ok", "data": {"count": project_links.count(), "data": project_data}})

    if verb == 'new':
        project = models.Project.objects.create(name=data['name'], description=data["description"])
        project.save()
        
        # Add LLM models to the project if provided
        if 'llm_models' in data and data['llm_models']:
            for model_id in data['llm_models']:
                try:
                    llm_model = models.LLMModel.objects.get(id=model_id)
                    project.llm_models.add(llm_model)
                except models.LLMModel.DoesNotExist:
                    # Skip invalid model IDs
                    pass
        
        membership = models.ProjectMembership.objects.create(user=request.user, project=project, role=models.Role.ADMIN)
        membership.save()
        return JsonResponse({"result": "ok"})

    return JsonResponse({"result": "failure", "data": {"message": f"unsupported verb: {verb}"}})
    

@login_required
def one_project_api(request, project_id):
    data = json.loads(request.body.decode('UTF-8'))
    verb = data.get('action', 'view')

    if verb == 'delete':
        project = models.Project.objects.filter(id=project_id).first()
        if not project:
            return JsonResponse({"result": "failure", "data": {"message": "not found"}})

        membership = models.ProjectMembership.objects.get(user=request.user, project=project)
        if membership.role != models.Role.ADMIN:
            return JsonResponse({"result": "failure", "data": {"message": "not an admin for this project"}})
        
        project.delete()
        return JsonResponse({"result": "ok"})

    return JsonResponse({"result": "failure", "data": {"message": f"unsupported verb: {verb}"}})
    

@login_required
def config_api(request):
    data = json.loads(request.body.decode('UTF-8'))
    clazz = data['class']

    if clazz == 'models':
        llm_models = models.LLMModel.objects.all()
        return JsonResponse({"result": "ok", "data": {"count": llm_models.count(), "data": [
            model.serialize() for model in llm_models
        ]}})

    return JsonResponse({"result": "failure", "data": {"message": "unknown config class"}})