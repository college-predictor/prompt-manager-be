from django import models
from enum import Enum
from auth.models import User


class LLMProvider(Enum):
    OPENAI = (1, )
    GOOGLE_GENAI = (2, )
    AMAZON_BEDROCK = (3, )
    AZURE = (4, )
    ANTHROPIC = (5, )

    @property
    def i(self):
        return self[0]


class Role(Enum):
    ADMIN = (0, )
    USER = (1, )

    @property
    def i(self):
        return self[0]


class LLMModel(models.Model):
    provider = models.IntegerField(choices=LLMProvider, null=False)
    name = models.CharField(max_length=50, null=False)

    def serialize(self):
        return {
            "name": self.name,
            "provider": self.provider.i
        }


class Project(models.Model):
    name = models.CharField(max_length=120, null=False)
    description = models.TextField(default=None)
    models = models.ManyToManyField(LLMModel, related_name='+')
    users = models.ManyToManyField(User, through='ProjectMembership', related_name='projects')
    

class ProjectMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.IntegerField(choices=Role, default=Role.USER)

    class Meta:
        unique_together = ('user', 'project')