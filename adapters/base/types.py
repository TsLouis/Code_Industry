from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel

class ModelProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False

class ChatResponse(BaseModel):
    id: str
    choices: List[Dict]
    usage: Optional[Dict] 