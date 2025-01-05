import pytest
from src.adapters.base.types import ModelConfig, ModelProvider
from src.adapters.providers.openai import create_openai_config

def test_create_openai_config():
    """测试创建OpenAI配置"""
    # 测试基本配置
    config = create_openai_config(
        api_key="test-key"
    )
    assert isinstance(config, ModelConfig)
    assert config.provider == ModelProvider.OPENAI
    assert config.model_name == "gpt-3.5-turbo"
    assert config.api_key == "test-key"
    assert config.temperature == 0.7

    # 测试自定义配置
    config = create_openai_config(
        api_key="test-key",
        model_name="gpt-4",
        base_url="https://custom-api.openai.com",
        temperature=0.9,
        max_tokens=1000,
        timeout=30,
        max_retries=5
    )
    assert config.model_name == "gpt-4"
    assert config.base_url == "https://custom-api.openai.com/v1"
    assert config.temperature == 0.9
    assert config.max_tokens == 1000
    assert config.timeout == 30
    assert config.max_retries == 5

def test_create_openai_config_validation():
    """测试OpenAI配置验证"""
    # 测试无效的API密钥
    with pytest.raises(ValueError):
        create_openai_config(api_key="") 