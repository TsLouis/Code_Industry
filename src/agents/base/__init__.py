"""
Base package for agents
"""

from .interface import BaseAgent
from .types import AgentConfig, AgentResponse, AgentRole, AgentError, Message

__all__ = [
    "BaseAgent",
    "AgentConfig",
    "AgentResponse",
    "AgentRole",
    "AgentError",
    "Message",
] 