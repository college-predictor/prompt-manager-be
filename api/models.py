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
    provider_name = models.IntegerField(choices=LLMProvider, null=False)
    description = models.TextField(default=None)
    temperature = models.FloatField(null=True, blank=True)
    max_tokens = models.IntegerField(null=True, blank=True)
    roles_allowed = models.JSONField(default=list)
    stream = models.BooleanField(default=False)
    top_p = models.FloatField(null=True, blank=True)
    top_k = models.IntegerField(null=True, blank=True)
    image_input = models.BooleanField(default=False)
    audio_input = models.BooleanField(default=False)

    def is_temperature_allowed(self) -> bool:
        return self.temperature is not None

    def is_max_tokens_allowed(self) -> bool:
        return self.max_tokens is not None

    def is_top_p_allowed(self) -> bool:
        return self.top_p is not None

    def is_top_k_allowed(self) -> bool:
        return self.top_k is not None
    
    def is_image_input_allowed(self) -> bool:
        return self.image_input
    
    def is_audio_input_allowed(self) -> bool:
        return self.audio_input

    def __str__(self) -> str:
        return (
            f"LLMModel(model_name='{self.model_name}', provider='{self.provider_name}', "
            f"temperature={self.temperature}, max_tokens={self.max_tokens}, top_p={self.top_p}, top_k={self.top_k}, "
            f"roles_allowed={self.roles_allowed}, image_input={self.image_input}, audio_input={self.audio_input})"
        )

    def serialize(self):
        return {
            "model_name": self.model_name,
            "provider_name": self.provider_name,
            "description": self.description,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "roles_allowed": self.roles_allowed,
            "image_input": self.image_input,
            "audio_input": self.audio_input
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