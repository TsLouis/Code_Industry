import openai
from typing import AsyncIterator
from ..base.interface import LLMProvider
from ..base.types import ChatRequest, ChatResponse

class OpenAIProvider(LLMProvider):
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai-proxy.org/v1",
        **kwargs
    ):
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            **kwargs
        )

    async def chat_completion(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        try:
            response = await self.client.chat.completions.create(
                model=request.model,
                messages=[{"role": m.role, "content": m.content} for m in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=False
            )
            return ChatResponse(
                id=response.id,
                choices=[{
                    "message": {"content": response.choices[0].message.content}
                }],
                usage=dict(response.usage)
            )
        except Exception as e:
            # 添加重试逻辑
            raise e

    async def stream_chat_completion(
        self,
        request: ChatRequest,
    ) -> AsyncIterator[ChatResponse]:
        try:
            response = await self.client.chat.completions.create(
                model=request.model,
                messages=[m.dict() for m in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True
            )
            async for chunk in response:
                yield ChatResponse(
                    id=chunk.id,
                    choices=chunk.choices,
                    usage=None
                )
        except Exception as e:
            # 添加重试逻辑
            raise e 