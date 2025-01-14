"""
LLM工具类，用于统一处理LLM调用
"""

from typing import Optional, Dict, Any, List
from src.adapters.base import BaseLLMAdapter, ModelResponse

class LLMTool:
    """LLM工具类"""
    
    def __init__(self, adapter: BaseLLMAdapter):
        """初始化
        
        Args:
            adapter: LLM适配器实例
        """
        self.adapter = adapter
        
    async def aask(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """异步调用LLM
        
        Args:
            prompt: 提示词
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Returns:
            str: LLM响应内容
        """
        try:
            # 构建消息
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            # 调用LLM
            response = await self.adapter.chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return response.content
            
        except Exception as e:
            raise Exception(f"LLM调用失败: {str(e)}")
            
    async def achat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """异步聊天
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Returns:
            ModelResponse: LLM响应
        """
        try:
            return await self.adapter.chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        except Exception as e:
            raise Exception(f"LLM聊天失败: {str(e)}") 