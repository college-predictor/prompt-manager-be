class Conversation(BaseModel):
    user_id: str
    messages: List[dict]  # List of message dicts with 'role' and 'content'
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    user_id: str
    