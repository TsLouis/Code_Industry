from anthropic import Anthropic
from typing import AsyncIterator
from ..base.interface import LLMProvider
from ..base.types import ChatRequest, ChatResponse

class AnthropicProvider(LLMProvider):
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai-proxy.org/anthropic",
        **kwargs
    ):
        self.client = Anthropic(
            api_key=api_key,
            base_url=base_url,
            **kwargs
        )

    async def chat_completion(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        try:
            response = await self.client.messages.create(
                model=request.model,
                messages=[m.dict() for m in request.messages],
                max_tokens=request.max_tokens,
                stream=False
            )
            return ChatResponse(
                id=response.id,
                choices=[{
                    "message": response.content[0].text,
                    "finish_reason": response.stop_reason
                }],
                usage=response.usage
            )
        except Exception as e:
            # 添加重试逻辑
            raise e

    async def stream_chat_completion(
        self,
        request: ChatRequest,
    ) -> AsyncIterator[ChatResponse]:
        try:
            response = await self.client.messages.create(
                model=request.model,
                messages=[m.dict() for m in request.messages],
                max_tokens=request.max_tokens,
                stream=True
            )
            async for chunk in response:
                yield ChatResponse(
                    id=chunk.id,
                    choices=[{
                        "delta": {"content": chunk.delta.text},
                        "finish_reason": chunk.stop_reason
                    }],
                    usage=None
                )
        except Exception as e:
            # 添加重试逻辑
            raise e 