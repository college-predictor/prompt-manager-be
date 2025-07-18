from pymongo import MongoClient
from django.conf import settings
from bson import ObjectId
from datetime import datetime
import json

class MongoService:
    def __init__(self):
        self.client = MongoClient(settings.MONGO_CONNECTION_STRING)
        self.db = self.client[settings.MONGO_DB_NAME]
        self.prompt_templates = self.db.prompt_templates

    def create_prompt_template(self, user_id, project_id, template_data):
        """
        Create a new prompt template
        """
        document = {
            'user_id': user_id,
            'project_id': project_id,
            'name': template_data.get('name'),
            'description': template_data.get('description', ''),
            'template': template_data.get('template', {}),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_active': True
        }
        
        result = self.prompt_templates.insert_one(document)
        return str(result.inserted_id)

    def get_prompt_templates(self, user_id, project_id=None):
        """
        Get prompt templates for a user, optionally filtered by project
        """
        query = {'user_id': user_id, 'is_active': True}
        if project_id:
            query['project_id'] = project_id
            
        templates = list(self.prompt_templates.find(query))
        
        # Convert ObjectId to string for JSON serialization
        for template in templates:
            template['_id'] = str(template['_id'])
            
        return templates

    def get_prompt_template_by_id(self, template_id, user_id):
        """
        Get a specific prompt template by ID
        """
        template = self.prompt_templates.find_one({
            '_id': ObjectId(template_id),
            'user_id': user_id,
            'is_active': True
        })
        
        if template:
            template['_id'] = str(template['_id'])
            
        return template

    def update_prompt_template(self, template_id, user_id, update_data):
        """
        Update a prompt template
        """
        update_data['updated_at'] = datetime.utcnow()
        
        result = self.prompt_templates.update_one(
            {'_id': ObjectId(template_id), 'user_id': user_id},
            {'$set': update_data}
        )
        
        return result.modified_count > 0

    def delete_prompt_template(self, template_id, user_id):
        """
        Soft delete a prompt template
        """
        result = self.prompt_templates.update_one(
            {'_id': ObjectId(template_id), 'user_id': user_id},
            {'$set': {'is_active': False, 'updated_at': datetime.utcnow()}}
        )
        
        return result.modified_count > 0

    def validate_template_structure(self, template_data):
        """
        Validate the structure of a prompt template
        """
        required_fields = ['temperature', 'max_tokens', 'model', 'messages']
        
        for field in required_fields:
            if field not in template_data:
                return False, f"Missing required field: {field}"
                
        # Validate messages structure
        if not isinstance(template_data['messages'], list):
            return False, "Messages must be a list"
            
        for message in template_data['messages']:
            if 'role' not in message or 'content' not in message:
                return False, "Each message must have 'role' and 'content' fields"
                
        return True, "Valid template structure"

# Global instance
mongo_service = MongoService()