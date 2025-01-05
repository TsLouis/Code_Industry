from typing import Optional
from src.adapters.base.types import ModelConfig, ModelProvider

DEFAULT_API_BASE = "https://api.openai-proxy.org/v1"

def create_openai_config(
    api_key: str,
    model_name: str = "gpt-3.5-turbo",
    base_url: Optional[str] = DEFAULT_API_BASE,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    timeout: int = 60,
    max_retries: int = 3
) -> ModelConfig:
    """创建 OpenAI 配置
    
    Args:
        api_key: API密钥
        model_name: 模型名称，默认为gpt-3.5-turbo
        base_url: API基础URL，默认为代理域名
        temperature: 温度参数，控制随机性
        max_tokens: 最大token数
        timeout: 超时时间(秒)
        max_retries: 最大重试次数
    """
    if not api_key:
        raise ValueError("API key is required")
        
    if base_url and not base_url.endswith("/v1"):
        base_url = f"{base_url}/v1"

    return ModelConfig(
        provider=ModelProvider.OPENAI,
        model_name=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
        max_retries=max_retries
    ) 