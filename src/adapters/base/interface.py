from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

from .types import ModelConfig, ModelResponse, ModelError

class BaseLLMAdapter(ABC):
    """LLM适配器基类"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self._client = None
        self._setup()
    
    @abstractmethod
    def _setup(self) -> None:
        """初始化客户端"""
        pass
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """聊天补全"""
        pass
    
    @abstractmethod
    async def completion(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """文本补全"""
        pass
    
    @abstractmethod
    async def embeddings(
        self,
        texts: List[str],
        **kwargs
    ) -> List[List[float]]:
        """文本嵌入"""
        pass
    
    def _validate_config(self) -> None:
        """验证配置"""
        if not self.config.api_key:
            raise ModelError("API key is required")
        if not self.config.model_name:
            raise ModelError("Model name is required") 