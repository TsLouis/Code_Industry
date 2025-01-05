"""
Base types for the agents module
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator


class AgentRole(str, Enum):
    """Agent role types"""
    COORDINATOR = "coordinator"
    PRODUCT_MANAGER = "product_manager"
    DEVELOPER = "developer"
    SYSTEM = "system"
    USER = "user"


class AgentError(Exception):
    """Base exception for agent errors"""
    pass


class Task(BaseModel):
    """Task model"""
    id: str
    description: str
    type: Optional[str] = None
    priority: Optional[int] = None
    status: str = "pending"
    metadata: Optional[Dict[str, Any]] = None


class ExecutionResult(BaseModel):
    """Execution result model"""
    status: str
    output: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Requirement(BaseModel):
    """Requirement model"""
    id: str
    description: str
    type: str
    priority: Optional[int] = None
    status: str = "pending"
    metadata: Optional[Dict[str, Any]] = None


class Specifications(BaseModel):
    """Specifications model"""
    functional: List[str] = []
    security: List[str] = []
    performance: List[str] = []
    metadata: Optional[Dict[str, Any]] = None


class UserStory(BaseModel):
    """User story model"""
    id: str
    title: str
    description: str
    acceptance_criteria: List[str] = []
    priority: Optional[int] = None
    status: str = "pending"
    metadata: Optional[Dict[str, Any]] = None


class TechnicalRequirement(BaseModel):
    """Technical requirement model"""
    id: str
    description: str
    type: str
    priority: Optional[int] = None
    status: str = "pending"
    dependencies: List[str] = []
    metadata: Optional[Dict[str, Any]] = None


class TechnicalDesign(BaseModel):
    """Technical design model"""
    components: List[str] = []
    apis: List[str] = []
    database: Dict[str, List[str]] = {}
    metadata: Optional[Dict[str, Any]] = None


class ImplementationStep(BaseModel):
    """Implementation step model"""
    id: str
    description: str
    code_path: str
    status: str = "pending"
    metadata: Optional[Dict[str, Any]] = None


class CodeChange(BaseModel):
    """Code change model"""
    file: str
    content: str
    type: str  # create, update, delete
    metadata: Optional[Dict[str, Any]] = None


class AgentConfig(BaseModel):
    """Configuration for an agent"""
    name: Optional[str] = None
    role: AgentRole
    description: Optional[str] = None
    instructions: Optional[str] = None
    tools: Optional[List[str]] = None
    llm_config: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class Message(BaseModel):
    """A message in the conversation"""
    role: AgentRole
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None

    @field_validator('content')
    def content_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('content must not be empty')
        return v


class AgentResponse(BaseModel):
    """Response from an agent"""
    messages: List[Message] = []
    response: str
    status: str = "completed"
    thoughts: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None 