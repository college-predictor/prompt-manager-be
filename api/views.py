import json
import api.models as models
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from .prompt_factory import PromptFactory
from django.core.exceptions import ValidationError

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
def prompt_factory_api(request, project_id):
    """API endpoint to get formatted prompt content using PromptFactory"""
    try:
        data = json.loads(request.body.decode('UTF-8'))
        prompt_name = data.get('prompt_name')
        variables = data.get('variables', {})
        provider_id = data.get('provider_id', None)
        model_name = data.get('model_name', None)

        if not prompt_name:
            return JsonResponse({
                "result": "failure", 
                "data": {"message": "prompt_name is required"}
            })
        
        # Validate that either both provider_id and model_name are provided or neither
        if (provider_id is None) != (model_name is None):
            return JsonResponse({
                "result": "failure",
                "data": {"message": "Both provider_id and model_name must be provided together, or neither should be provided"}
            })
        
        # Create PromptFactory instance
        factory = PromptFactory(
            prompt_name=prompt_name,
            user=request.user,
            project_id=project_id,
            variables=variables
        )
        
        # Build the formatted prompt
        prompt_data = factory.build_prompt(provider_id, model_name)
        
        return JsonResponse({
            "result": "ok", 
            "data": prompt_data
        })
        
    except ValidationError as e:
        return JsonResponse({
            "result": "failure", 
            "data": {"message": str(e)}
        })
    except Exception as e:
        return JsonResponse({
            "result": "failure", 
            "data": {"message": f"Error processing request: {str(e)}"}
        })
    

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


# Helper function to check project membership
def _check_project_access(user, project_id):
    try:
        project = models.Project.objects.get(id=project_id)
        membership = models.ProjectMembership.objects.get(user=user, project=project)
        return project, membership
    except (models.Project.DoesNotExist, models.ProjectMembership.DoesNotExist):
        return None, None


# PromptCollection API endpoints
@login_required
def collections_api(request, project_id):
    """Handle CRUD operations for prompt collections within a project"""
    data = json.loads(request.body.decode('UTF-8'))
    verb = data.get('action', 'list')
    
    # Check project access
    project, membership = _check_project_access(request.user, project_id)
    if not project:
        return JsonResponse({"result": "failure", "data": {"message": "Project not found or access denied"}})
    
    if verb == 'list':
        collections = models.PromptCollection.objects.filter(project=project)
        collection_data = []
        
        for collection in collections:
            collection_data.append({
                'id': collection.id,
                'name': collection.name,
                'description': collection.description,
                'created_at': collection.created_at.isoformat(),
                'prompt_count': collection.prompts.count()
            })
        
        return JsonResponse({"result": "ok", "data": {"count": collections.count(), "data": collection_data}})
    
    if verb == 'new':
        try:
            collection = models.PromptCollection.objects.create(
                name=data['name'],
                description=data.get('description', ''),
                project=project
            )
            return JsonResponse({"result": "ok", "data": {
                'id': collection.id,
                'name': collection.name,
                'description': collection.description,
                'created_at': collection.created_at.isoformat(),
                'updated_at': collection.updated_at.isoformat()
            }})
        except IntegrityError:
            return JsonResponse({"result": "failure", "data": {"message": "Collection name already exists in this project"}})
    
    return JsonResponse({"result": "failure", "data": {"message": f"unsupported verb: {verb}"}})


@login_required
def one_collection_api(request, project_id, collection_id):
    """Handle operations for a specific collection"""
    data = json.loads(request.body.decode('UTF-8'))
    verb = data.get('action', 'view')
    
    # Check project access
    project, membership = _check_project_access(request.user, project_id)
    if not project:
        return JsonResponse({"result": "failure", "data": {"message": "Project not found or access denied"}})
    
    # Get collection
    collection = get_object_or_404(models.PromptCollection, id=collection_id, project=project)
    
    if verb == 'view':
        prompts = collection.prompts.all()
        prompt_data = []
        
        for prompt in prompts:
            prompt_data.append({
                'id': prompt.id,
                'name': prompt.name,
                'description': prompt.description,
                'template': prompt.template,
                'created_at': prompt.created_at.isoformat(),
                'updated_at': prompt.updated_at.isoformat()
            })
        
        return JsonResponse({"result": "ok", "data": {
            'id': collection.id,
            'name': collection.name,
            'description': collection.description,
            'created_at': collection.created_at.isoformat(),
            'updated_at': collection.updated_at.isoformat(),
            'prompts': prompt_data
        }})
    
    if verb == 'update':
        try:
            if 'name' in data:
                collection.name = data['name']
            if 'description' in data:
                collection.description = data['description']
            collection.save()
            
            return JsonResponse({"result": "ok", "data": {
                'id': collection.id,
                'name': collection.name,
                'description': collection.description,
                'updated_at': collection.updated_at.isoformat()
            }})
        except IntegrityError:
            return JsonResponse({"result": "failure", "data": {"message": "Collection name already exists in this project"}})
    
    if verb == 'delete':
        collection.delete()
        return JsonResponse({"result": "ok"})
    
    return JsonResponse({"result": "failure", "data": {"message": f"unsupported verb: {verb}"}})


# PromptTemplate API endpoints
@login_required
def prompts_api(request, project_id):
    """Handle CRUD operations for prompts within a project"""
    data = json.loads(request.body.decode('UTF-8'))
    verb = data.get('action', 'list')
    
    # Check project access
    project, membership = _check_project_access(request.user, project_id)
    if not project:
        return JsonResponse({"result": "failure", "data": {"message": "Project not found or access denied"}})
    
    if verb == 'list':
        prompts = models.PromptTemplate.objects.filter(project=project)
        prompt_data = []
        
        for prompt in prompts:
            prompt_data.append({
                'id': prompt.id,
                'name': prompt.name,
                'description': prompt.description,
                'collection_id': prompt.collection.id if prompt.collection else None,
                'collection_name': prompt.collection.name if prompt.collection else None,
                'model_name': prompt.llm_model.model_name,
                'llm_provider': models.LLMProvider(prompt.llm_provider).label,
                'messages': prompt.messages,
                'temperature': prompt.temperature,
                'max_tokens': prompt.max_tokens,
                'top_p': prompt.top_p,
                'top_k': prompt.top_k,
                'frequency_penalty': prompt.frequency_penalty,
                'presence_penalty': prompt.presence_penalty,
                'created_at': prompt.created_at.isoformat(),
                'updated_at': prompt.updated_at.isoformat()
            })
        
        return JsonResponse({"result": "ok", "data": {"count": prompts.count(), "data": prompt_data}})
    
    if verb == 'new':
        try:
            # Check if collection exists if provided
            collection = None
            if 'collection_id' in data and data['collection_id']:
                collection = get_object_or_404(models.PromptCollection, id=data['collection_id'], project=project)
            
            # Get LLM model
            llm_model = get_object_or_404(models.LLMModel, id=data['llm_model'])
            
            prompt = models.PromptTemplate.objects.create(
                name=data['name'],
                description=data.get('description', ''),
                project=project,
                collection=collection,
                llm_model=llm_model,
                llm_provider=models.LLMProvider[data['llm_provider'].upper()].value,
                messages=data.get('messages', {}),
                temperature=data.get('temperature'),
                max_tokens=data.get('max_tokens'),
                top_p=data.get('top_p'),
                top_k=data.get('top_k'),
                frequency_penalty=data.get('frequency_penalty'),
                presence_penalty=data.get('presence_penalty')
            )
            
            return JsonResponse({"result": "ok", "data": {
                'id': prompt.id,
                'name': prompt.name,
                'description': prompt.description,
                'collection_id': prompt.collection.id if prompt.collection else None,
                'collection_name': prompt.collection.name if prompt.collection else None,
                'llm_model': prompt.llm_model.serialize(),
                'llm_provider': models.LLMProvider(prompt.llm_provider).label,
                'messages': prompt.messages,
                'temperature': prompt.temperature,
                'max_tokens': prompt.max_tokens,
                'top_p': prompt.top_p,
                'top_k': prompt.top_k,
                'frequency_penalty': prompt.frequency_penalty,
                'presence_penalty': prompt.presence_penalty,
                'created_at': prompt.created_at.isoformat(),
                'updated_at': prompt.updated_at.isoformat()
            }})
        except IntegrityError:
            return JsonResponse({"result": "failure", "data": {"message": "Prompt name already exists in this project"}})
    
    return JsonResponse({"result": "failure", "data": {"message": f"unsupported verb: {verb}"}})


@login_required
def one_prompt_api(request, project_id, prompt_id):
    """Handle operations for a specific prompt"""
    data = json.loads(request.body.decode('UTF-8'))
    verb = data.get('action', 'view')
    
    # Check project access
    project, membership = _check_project_access(request.user, project_id)
    if not project:
        return JsonResponse({"result": "failure", "data": {"message": "Project not found or access denied"}})
    
    # Get prompt
    prompt = get_object_or_404(models.PromptTemplate, id=prompt_id, project=project)
    
    if verb == 'view':
        return JsonResponse({"result": "ok", "data": {
            'id': prompt.id,
            'name': prompt.name,
            'description': prompt.description,
            'collection_id': prompt.collection.id if prompt.collection else None,
            'collection_name': prompt.collection.name if prompt.collection else None,
            'llm_model': prompt.llm_model.serialize(),
            'llm_provider': models.LLMProvider(prompt.llm_provider).label,
            'messages': prompt.messages,
            'temperature': prompt.temperature,
            'max_tokens': prompt.max_tokens,
            'top_p': prompt.top_p,
            'top_k': prompt.top_k,
            'frequency_penalty': prompt.frequency_penalty,
            'presence_penalty': prompt.presence_penalty,
            'created_at': prompt.created_at.isoformat(),
            'updated_at': prompt.updated_at.isoformat()
        }})
    
    if verb == 'update':
        try:
            if 'name' in data:
                prompt.name = data['name']
            if 'description' in data:
                prompt.description = data['description']
            if 'llm_model' in data:
                llm_model = get_object_or_404(models.LLMModel, id=data['llm_model'])
                prompt.llm_model = llm_model
            if 'llm_provider' in data:
                prompt.llm_provider = data['llm_provider']
            if 'messages' in data:
                prompt.messages = data['messages']
            if 'temperature' in data:
                prompt.temperature = data['temperature']
            if 'max_tokens' in data:
                prompt.max_tokens = data['max_tokens']
            if 'top_p' in data:
                prompt.top_p = data['top_p']
            if 'top_k' in data:
                prompt.top_k = data['top_k']
            if 'frequency_penalty' in data:
                prompt.frequency_penalty = data['frequency_penalty']
            if 'presence_penalty' in data:
                prompt.presence_penalty = data['presence_penalty']
            if 'collection_id' in data:
                if data['collection_id']:
                    collection = get_object_or_404(models.PromptCollection, id=data['collection_id'], project=project)
                    prompt.collection = collection
                else:
                    prompt.collection = None
            
            prompt.save()
            
            return JsonResponse({"result": "ok", "data": {
                'id': prompt.id,
                'name': prompt.name,
                'description': prompt.description,
                'collection_id': prompt.collection.id if prompt.collection else None,
                'collection_name': prompt.collection.name if prompt.collection else None,
                'llm_model': prompt.llm_model.serialize(),
                'llm_provider': models.LLMProvider(prompt.llm_provider).label,
                'messages': prompt.messages,
                'temperature': prompt.temperature,
                'max_tokens': prompt.max_tokens,
                'top_p': prompt.top_p,
                'top_k': prompt.top_k,
                'frequency_penalty': prompt.frequency_penalty,
                'presence_penalty': prompt.presence_penalty,
                'updated_at': prompt.updated_at.isoformat()
            }})
        except IntegrityError:
            return JsonResponse({"result": "failure", "data": {"message": "Prompt name already exists in this project"}})
    
    if verb == 'delete':
        prompt.delete()
        return JsonResponse({"result": "ok"})
    
    return JsonResponse({"result": "failure", "data": {"message": f"unsupported verb: {verb}"}})


