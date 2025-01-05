from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator

class ModelProvider(str, Enum):
    """模型提供商枚举"""
    OPENAI = "openai"
    AZURE = "azure"
    ANTHROPIC = "anthropic"
    ZHIPU = "zhipu"
    MOONSHOT = "moonshot"

class ModelConfig(BaseModel):
    """模型配置"""
    provider: ModelProvider
    model_name: str = Field(..., min_length=1)
    api_key: str = Field(..., min_length=1)
    base_url: Optional[str] = None
    timeout: int = Field(default=60, gt=0)
    max_retries: int = Field(default=3, ge=0)
    temperature: float = Field(default=0.7, ge=0, le=1)
    max_tokens: int = Field(default=4096, gt=0)
    extra_params: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v):
        if not isinstance(v, ModelProvider):
            raise ValueError(f"Invalid provider: {v}")
        return v

class ModelResponse(BaseModel):
    """模型响应"""
    content: str = Field(..., min_length=1)
    role: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    usage: Dict[str, Any]
    raw_response: Dict[str, Any]

class ModelError(Exception):
    """模型错误"""
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message) 