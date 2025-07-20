from typing import List, Dict, Any
from .models import PromptTemplate, Project, LLMProvider
from authen.models import User
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
import re
from typing import Dict, Any, List


class PromptFactory:
    def __init__(self, prompt_name: str, user: User, project_id: int, variables: dict = None):
        self.prompt_name = prompt_name
        self.user = user
        self.project_id = project_id
        self.variables = variables or {}
        self._template: PromptTemplate = self.get_prompt_template()
    
    def get_prompt_template(self) -> PromptTemplate:
        """Retrieve the prompt template for the user and project"""
        project = get_object_or_404(Project, id=self.project_id)
        # Get the prompt template
        _template = get_object_or_404(
            PromptTemplate, 
            name=self.prompt_name, 
            project=project
        )
        
        return _template
    
    def process_messages(self):
        """Process template messages and separate them by role"""
        processed_messages = {}
        for role in self._template.messages:
            processed_messages[role] = []
            for text in self._template.messages[role]:
                processed_messages[role].append(text.format(**self.variables))
        return processed_messages
    
    def get_openai_content(self, model_name: str = None) -> Dict[str, Any]:
        """Format content for OpenAI API."""
        def format_messages(messages: List[str], role: str) -> Dict[str, Any]:
            return {
                "role": role,
                "content": [{"type": "input_text", "text": msg} for msg in messages]
            }

        processed_messages = self.process_messages()
        messages = []
        for role in processed_messages:
            messages.append(format_messages(processed_messages.get(role), role))

        content = {
            "model": model_name if model_name else self._template.llm_model.model_name,
            "input": messages
        }
        if self._template.temperature:
            content["temperature"] = self._template.temperature
        if self._template.max_tokens:
            content["max_output_tokens"] = self._template.max_tokens
        if self._template.top_p:
            content["top_p"] = self._template.top_p
        if self._template.top_k:
            content["top_k"] = self._template.top_k
        if self._template.frequency_penalty:
            content["frequency_penalty"] = self._template.frequency_penalty
        if self._template.presence_penalty:
            content["presence_penalty"] = self._template.presence_penalty
        return content
        
    def get_anthropic_content(self, model_name: str = None) -> Dict[str, Any]:
        """Format content for Anthropic API."""
        def format_messages(messages: List[str], role: str) -> Dict[str, Any]:
            return {
                "role": role,
                "content": [{"type": "text", "text": msg} for msg in messages]
            }
            
        processed_messages = self.process_messages()
        content = {
            "model": model_name if model_name else self._template.llm_model.model_name
        }
        messages = []
        for role in processed_messages:
            messages.append(format_messages(processed_messages[role], role))
        content["messages"] = messages
        if self._template.temperature:
            content["temperature"] = self._template.temperature
        if self._template.max_tokens:
            content["max_tokens"] = self._template.max_tokens
        else:
            content["max_tokens"] = 19900
        if self._template.top_p:
            content["top_p"] = self._template.top_p
        if self._template.top_k:
            content["top_k"] = self._template.top_k
        if self._template.frequency_penalty:
            content["frequency_penalty"] = self._template.frequency_penalty
        if self._template.presence_penalty:
            content["presence_penalty"] = self._template.presence_penalty
        return content
        
    def get_genai_content(self, model_name: str = None) -> Dict[str, Any]:
        """Format content for Google GenAI API."""
        processed_messages = self.process_messages()
        content = {
            "model": model_name if model_name else self._template.llm_model.model_name,
            "config": {}
        }
        if processed_messages.get("system"):
            content["config"]["system_instruction"] = "\n".join(processed_messages["system"])
        if processed_messages.get("user"):
            content["contents"] = processed_messages["user"]
        if self._template.temperature:
            content["config"]["temperature"] = self._template.temperature
        if self._template.max_tokens:
            content["config"]["max_output_tokens"] = self._template.max_tokens
        if self._template.top_p:
            content["config"]["top_p"] = self._template.top_p
        if self._template.top_k:
            content["config"]["top_k"] = self._template.top_k
        if self._template.frequency_penalty:
            content["config"]["frequency_penalty"] = self._template.frequency_penalty
        if self._template.presence_penalty:
            content["config"]["presence_penalty"] = self._template.presence_penalty
        return content
    
    def get_provider_content(self, provider_id: int = None, model_name: str = None) -> Dict[str, Any]:
        """Get formatted content based on the LLM provider"""
        template = self.get_prompt_template()
        
        if not provider_id:
            provider_id = template.llm_model.provider_id
        
        if provider_id == LLMProvider.OPENAI:
            return self.get_openai_content(model_name)
        elif provider_id == LLMProvider.ANTHROPIC:
            return self.get_anthropic_content(model_name)
        elif provider_id == LLMProvider.GOOGLE_GENAI:
            return self.get_genai_content(model_name)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_id}")
    
    def build_prompt(self, provider_id: int = None, model_name: str = None) -> Dict[str, Any]:
        """Build the complete prompt with provider-specific formatting"""
        template = self.get_prompt_template()
        return {
            'template_name': template.name,
            'template': self.get_provider_content(provider_id, model_name)
        }


