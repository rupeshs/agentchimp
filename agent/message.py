from typing import Optional, List, Dict
from pydantic import BaseModel


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: Dict


class Message(BaseModel):
    role: str  # system, user, assistant, tool
    content: Optional[str] = None
    tool_calls: List[ToolCall] = []
    tool_call_id: Optional[str] = None
