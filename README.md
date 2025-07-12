# Prompt Manager Backend

A Django REST API for managing AI prompts and projects with LLM model integration.

## Features

- Google Firebase Authentication
- Project management with role-based access control
- LLM model configuration and association
- RESTful API endpoints
- CORS support for frontend integration

## Prerequisites

- Python 3.8+
- Django 4.x
- Google Firebase project for authentication

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd prompt-manager-be
```

### 2. Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the root directory:
```env
DJ_SECRET_KEY=your-django-secret-key-here
FIREBASE_SA_FILE=path/to/your/firebase-service-account.json
```

### 5. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 7. Run the Development Server
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## API Endpoints

### Authentication Endpoints

#### POST /auth/login
Authenticate user with Google Firebase token.

**Request Body:**
```json
{
  "auth_type": 1,
  "token": "firebase-id-token"
}
```

**Response:**
```json
{
  "result": "ok",
  "data": {
    "email": "user@example.com",
    "name": "User Name"
  }
}
```

#### POST /auth/logout
Log out the current user.

**Response:**
```json
{
  "result": "ok"
}
```

### Project Management Endpoints

#### POST /api/projects
List all projects or create a new project.

**List Projects:**
```json
{
  "action": "list"
}
```

**Response:**
```json
{
  "result": "ok",
  "data": {
    "count": 2,
    "data": [
      {
        "role": 0,
        "name": "Project Name",
        "description": "Project description",
        "models": [
          {
            "model_name": "gpt-4",
            "provider_name": 1,
            "description": "OpenAI GPT-4",
            "temperature": 0.7,
            "max_tokens": 4000,
            "top_p": 1.0,
            "top_k": null,
            "roles_allowed": [0, 1, 2, 3],
            "image_input": true,
            "audio_input": false
          }
        ]
      }
    ]
  }
}
```

**Create New Project:**
```json
{
  "action": "new",
  "name": "My New Project",
  "description": "Project description",
  "llm_models": [1, 2, 3]
}
```

**Response:**
```json
{
  "result": "ok"
}
```

#### POST /api/projects/{project_id}
Manage individual project operations.

**Delete Project:**
```json
{
  "action": "delete"
}
```

**Response:**
```json
{
  "result": "ok"
}
```

**Error Responses:**
```json
{
  "result": "failure",
  "data": {
    "message": "not found"
  }
}
```

```json
{
  "result": "failure",
  "data": {
    "message": "not an admin for this project"
  }
}
```

#### POST /api/config
Retrieve configuration data.

**Get LLM Models:**
```json
{
  "class": "models"
}
```

**Response:**
```json
{
  "result": "ok",
  "data": {
    "count": 5,
    "data": [
      {
        "model_name": "gpt-4",
        "provider_name": 1,
        "description": "OpenAI GPT-4",
        "temperature": 0.7,
        "max_tokens": 4000,
        "top_p": 1.0,
        "top_k": null,
        "roles_allowed": [0, 1, 2, 3],
        "image_input": true,
        "audio_input": false
      }
    ]
  }
}
```

## Data Models

### LLM Providers
- `1`: OpenAI
- `2`: Google GenAI
- `3`: Amazon Bedrock
- `4`: Azure
- `5`: Anthropic

### User Roles
- `0`: Admin
- `1`: User

### LLM Roles
- `0`: Assistant
- `1`: User
- `2`: Developer
- `3`: System

## Authentication

All API endpoints (except auth endpoints) require authentication. The API uses Django's session-based authentication with Google Firebase token verification.

### Required Headers
- `Content-Type: application/json`
- Valid session cookie (set automatically after login)

## Error Handling

All endpoints return responses in the following format:

**Success:**
```json
{
  "result": "ok",
  "data": { ... }
}
```

**Failure:**
```json
{
  "result": "failure",
  "data": {
    "message": "error description"
  }
}
```

## Development

### Project Structure
```
prompt-manager-be/
├── api/                 # Main API app
│   ├── models.py       # Data models
│   ├── views.py        # API endpoints
│   └── urls.py         # URL routing
├── authen/             # Authentication app
│   ├── backend.py      # Firebase auth backend
│   ├── middleware.py   # CORS middleware
│   ├── models.py       # User model
│   └── views.py        # Auth endpoints
├── promptmanager/      # Django project settings
├── manage.py           # Django management script
└── requirements.txt    # Python dependencies
```

### Adding New Endpoints

1. Add view functions to `api/views.py`
2. Add URL patterns to `api/urls.py`
3. Apply `@login_required` decorator for protected endpoints
4. Follow the existing JSON response format

### Database Migrations

After modifying models:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Security Notes

- All sensitive data should be stored in environment variables
- Firebase service account file should be kept secure
- CORS is configured for development - adjust for production
- Session-based authentication is used - consider JWT for stateless architecture

## Production Deployment

1. Set `DEBUG = False` in settings.py
2. Configure proper `ALLOWED_HOSTS`
3. Use environment variables for all secrets
4. Set up proper database (PostgreSQL recommended)
5. Configure static file serving
6. Set up proper logging
7. Use HTTPS in production