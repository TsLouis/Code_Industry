from typing import AsyncIterator, Optional
import openai
from utils.logger import setup_logger

logger = setup_logger(__name__)

class OpenAIProvider:
    """OpenAI API提供者"""
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.client = openai.AsyncClient(
            api_key=api_key,
            base_url=base_url
        )
        self.logger = logger

    async def chat(self, messages: list, model: str = "gpt-3.5-turbo") -> AsyncIterator[str]:
        """与模型对话"""
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True
            )
            
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            self.logger.error(f"OpenAI API调用失败: {e}", exc_info=True)
            yield f"Error: {str(e)}" 