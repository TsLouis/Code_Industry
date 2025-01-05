from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from ...base.types import ModelConfig, ModelResponse, ModelError

class OpenAIAdapter:
    """OpenAI适配器"""
    
    def __init__(self, config: ModelConfig):
        """初始化适配器
        
        Args:
            config: 模型配置
        """
        self.config = config
        self._client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout,
            max_retries=config.max_retries
        )
        
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """聊天补全实现"""
        retries = 0
        last_error = None
        
        while retries <= self.config.max_retries:
            try:
                response = await self._client.chat.completions.create(
                    model=self.config.model_name,
                    messages=messages,
                    temperature=temperature or self.config.temperature,
                    max_tokens=max_tokens or self.config.max_tokens,
                    **{**self.config.extra_params, **kwargs}
                )

                return ModelResponse(
                    content=response.choices[0].message.content,
                    role=response.choices[0].message.role,
                    model=response.model,
                    usage=response.usage.model_dump(),
                    raw_response=response.model_dump()
                )
            except Exception as e:
                last_error = e
                retries += 1
                if retries > self.config.max_retries:
                    break
                continue
                
        raise ModelError(
            message=f"OpenAI API error after {retries} retries: {str(last_error)}",
            code="max_retries_exceeded",
            details={"retries": retries, "original_error": str(last_error)}
        )

    async def completion(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """文本补全实现"""
        retries = 0
        last_error = None
        
        while retries <= self.config.max_retries:
            try:
                response = await self._client.completions.create(
                    model=self.config.model_name,
                    prompt=prompt,
                    temperature=temperature or self.config.temperature,
                    max_tokens=max_tokens or self.config.max_tokens,
                    **{**self.config.extra_params, **kwargs}
                )

                return ModelResponse(
                    content=response.choices[0].text,
                    role="assistant",
                    model=response.model,
                    usage=response.usage.model_dump(),
                    raw_response=response.model_dump()
                )
            except Exception as e:
                last_error = e
                retries += 1
                if retries > self.config.max_retries:
                    break
                continue
                
        raise ModelError(
            message=f"OpenAI API error after {retries} retries: {str(last_error)}",
            code="max_retries_exceeded",
            details={"retries": retries, "original_error": str(last_error)}
        )

    async def embeddings(
        self,
        texts: List[str],
        **kwargs
    ) -> List[List[float]]:
        """文本嵌入实现"""
        retries = 0
        last_error = None
        
        while retries <= self.config.max_retries:
            try:
                response = await self._client.embeddings.create(
                    model=self.config.model_name,
                    input=texts,
                    **{**self.config.extra_params, **kwargs}
                )

                return [data.embedding for data in response.data]
            except Exception as e:
                last_error = e
                retries += 1
                if retries > self.config.max_retries:
                    break
                continue
                
        raise ModelError(
            message=f"OpenAI API error after {retries} retries: {str(last_error)}",
            code="max_retries_exceeded",
            details={"retries": retries, "original_error": str(last_error)}
        ) 