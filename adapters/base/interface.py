from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional
from .types import ChatRequest, ChatResponse

class LLMProvider(ABC):
    """LLM供应商基础接口"""
    
    @abstractmethod
    async def chat_completion(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        """同步聊天补全"""
        pass

    @abstractmethod
    async def stream_chat_completion(
        self,
        request: ChatRequest,
    ) -> AsyncIterator[ChatResponse]:
        """流式聊天补全"""
        pass 