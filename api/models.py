from django.db import models
from authen.models import User


class LLMProvider(models.IntegerChoices):
    OPENAI = (1, "OpenAI")
    GOOGLE_GENAI = (2, "Google GenAI")
    AMAZON_BEDROCK = (3, "Amazon Bedrock")
    AZURE = (4, "Azure")
    ANTHROPIC = (5, "Anthropic")


class Role(models.IntegerChoices):
    ADMIN = (0, "Admin")
    USER = (1, "User")


class LLMRoles(models.IntegerChoices):
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
            "temperature": self.temperature_allowed,
            "max_tokens": self.has_max_token_limit,
            "top_p": self.top_p_allowed,
            "top_k": self.top_k_allowed,
            "roles_allowed": self.roles_allowed,
            "image_input": self.image_input_allowed,
            "audio_input": self.audio_input_allowed
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