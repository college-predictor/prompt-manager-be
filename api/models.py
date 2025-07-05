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


class LLMModel(models.Model):
    provider = models.IntegerField(choices=LLMProvider, null=False)
    name = models.CharField(max_length=50, null=False)

    def serialize(self):
        return {
            "name": self.name,
            "provider": self.provider
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