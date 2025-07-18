from django.db import models
from authen.models import User


class LLMProvider(models.IntegerChoices):
    OPENAI = (1, "OpenAI")
    GOOGLE_GENAI = (2, "Google GenAI")
    ANTHROPIC = (3, "Anthropic")
    AZURE = (4, "Azure")


class Role(models.IntegerChoices):
    ADMIN = (0, "Admin")
    USER = (1, "User")


class LLMRoles(models.IntegerChoices):
    INSTRUCTION = (4, "instruction")
    SYSTEM = (3, "system")
    DEVELOPER = (2, "developer")
    USER = (1, "user")
    ASSISTANT = (0, "assistant")


class LLMModel(models.Model):
    model_name = models.CharField(max_length=50, null=False)
    provider_id = models.IntegerField(choices=LLMProvider, null=False)
    description = models.TextField(default=None)
    has_max_token_limit = models.IntegerField(null=True, blank=True)
    temperature_allowed = models.BooleanField(default=False)
    roles_allowed = models.JSONField(default=list)
    top_p_allowed = models.BooleanField(default=False)
    top_k_allowed = models.BooleanField(default=False)
    image_input_allowed = models.BooleanField(default=False)
    audio_input_allowed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return (
            f"LLMModel(model_name='{self.model_name}', provider_id='{self.provider_id}', "
            f"temperature={self.temperature_allowed}, max_tokens={self.has_max_token_limit}, top_p={self.top_p_allowed}, top_k={self.top_k_allowed}, "
            f"roles_allowed={self.roles_allowed}, image_input={self.image_input_allowed}, audio_input={self.audio_input_allowed})"
        )

    def serialize(self):
        return {
            "id": self.id,
            "model_name": self.model_name,
            "provider_id": self.provider_id,
            "provider_name": LLMProvider(self.provider_id).label,
            "description": self.description,
            "temperature_allowed": self.temperature_allowed,
            "has_max_token_limit": self.has_max_token_limit,
            "top_p_allowed": self.top_p_allowed,
            "top_k_allowed": self.top_k_allowed,
            "roles_allowed": self.roles_allowed,
            "image_input_allowed": self.image_input_allowed,
            "audio_input_allowed": self.audio_input_allowed,
        }


class Project(models.Model):
    name = models.CharField(max_length=120, null=False)
    description = models.TextField(default=None)
    llm_models = models.ManyToManyField(LLMModel, related_name='+')
    users = models.ManyToManyField(User, through='ProjectMembership', related_name='projects')
    

class ProjectMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.IntegerField(choices=Role, default=Role.USER)

    class Meta:
        unique_together = ('user', 'project')


class PromptCollection(models.Model):
    name = models.CharField(max_length=120, null=False)
    description = models.TextField(default=None, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='prompt_collections')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('name', 'project')
    
    def __str__(self):
        return f"PromptCollection(name='{self.name}', project='{self.project.name}')"


class PromptTemplate(models.Model):
    name = models.CharField(max_length=120, null=False)
    description = models.TextField(default=None, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='prompt_templates')
    collection = models.ForeignKey(PromptCollection, on_delete=models.CASCADE, related_name='prompts', null=True, blank=True)
    template = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'project')
    
    def __str__(self):
        return f"PromptTemplate(name='{self.name}', project='{self.project.name}', collection='{self.collection.name if self.collection else None}')"