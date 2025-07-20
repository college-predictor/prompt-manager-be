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
    roles_allowed = models.JSONField(default=list)
    has_max_token_limit = models.IntegerField(null=True, blank=True)
    temperature_allowed = models.BooleanField(default=False)
    top_p_allowed = models.BooleanField(default=False)
    top_k_allowed = models.BooleanField(default=False)
    frequency_penalty_allowed = models.BooleanField(default=False)
    presence_penalty_allowed = models.BooleanField(default=False)
    automatic_caching = models.BooleanField(default=True)
    image_input_allowed = models.BooleanField(default=False)
    audio_input_allowed = models.BooleanField(default=False)

    def serialize(self):
        return {
            "id": self.id,
            "model_name": self.model_name,
            "provider_id": self.provider_id,
            "provider_name": LLMProvider(self.provider_id).label,
            "description": self.description,
            "roles_allowed": self.roles_allowed,
            "temperature_allowed": self.temperature_allowed,
            "has_max_token_limit": self.has_max_token_limit,
            "top_p_allowed": self.top_p_allowed,
            "top_k_allowed": self.top_k_allowed,
            "frequency_penalty_allowed": self.frequency_penalty_allowed,
            "presence_penalty_allowed": self.presence_penalty_allowed,
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
    
    class Meta:
        unique_together = ('name', 'project')
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "project": {
                "id": self.project.id,
                "name": self.project.name
            },
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class PromptTemplate(models.Model):
    # Basic information
    name = models.CharField(max_length=120, null=False, help_text="Name of the prompt template")
    description = models.TextField(default=None, blank=True, help_text="Description of the prompt template")

    # Relationships
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='prompt_templates',help_text="Project this template belongs to")
    collection = models.ForeignKey(PromptCollection, on_delete=models.CASCADE, related_name='prompts', null=True, blank=True,help_text="Collection this template belongs to (optional)")

    # LLM Configuration
    llm_model = models.ForeignKey(LLMModel, on_delete=models.CASCADE, null=False, related_name='templates', help_text="The LLM model to use for this template")
    llm_provider = models.IntegerField(choices=LLMProvider, null=False, help_text="The LLM provider to use for this template")
    messages = models.JSONField(default=dict, help_text="Structured messages for the LLM conversation")

    # Model Parameters
    temperature = models.FloatField(null=True, help_text="Controls randomness in the output (0.0 to 2.0)")
    max_tokens = models.PositiveIntegerField(null=True, help_text="Maximum number of tokens in the response")
    top_p = models.FloatField(null=True, help_text="Nucleus sampling parameter (0.0 to 1.0)")
    top_k = models.PositiveIntegerField(null=True, help_text="Number of highest probability tokens to consider")
    frequency_penalty = models.FloatField(null=True, help_text="Penalty for frequent tokens (-2.0 to 2.0)")
    presence_penalty = models.FloatField(null=True, help_text="Penalty for new tokens (-2.0 to 2.0)")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'project')
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "project": {
                "id": self.project.id,
                "name": self.project.name
            },
            "collection": {
                "id": self.collection.id,
                "name": self.collection.name
            } if self.collection else None,
            "llm_model": self.llm_model.serialize(),
            "llm_provider": LLMProvider(self.llm_provider).label,
            "messages": self.messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

