from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Union
from typing import List


class ConversationAnalyzer(BaseModel):
    transcript: List[Dict[str, str]]
    latest_message: MessageModel
    agent_type: str
    client_details: ClientDetailsModel
    output_channel: List[str]
    response_channel: List[str] = Field(default=[])
    history: Optional[str] = Field(default=None)