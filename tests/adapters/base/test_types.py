import pytest
from src.adapters.base.types import ModelProvider, ModelConfig, ModelError

def test_model_provider_enum():
    """测试模型提供商枚举"""
    assert ModelProvider.OPENAI == "openai"
    assert ModelProvider.AZURE == "azure"
    assert ModelProvider.ANTHROPIC == "anthropic"
    assert ModelProvider.ZHIPU == "zhipu"
    assert ModelProvider.MOONSHOT == "moonshot"

def test_model_config():
    """测试模型配置"""
    config = ModelConfig(
        provider=ModelProvider.OPENAI,
        model_name="gpt-3.5-turbo",
        api_key="test-key"
    )
    assert config.provider == ModelProvider.OPENAI
    assert config.model_name == "gpt-3.5-turbo"
    assert config.api_key == "test-key"
    assert config.timeout == 60
    assert config.max_retries == 3
    assert config.temperature == 0.7
    assert config.max_tokens == 4096
    assert config.extra_params == {}

def test_model_error():
    """测试模型错误"""
    error = ModelError(
        message="Test error",
        code="test_error",
        details={"test": "value"}
    )
    assert str(error) == "Test error"
    assert error.message == "Test error"
    assert error.code == "test_error"
    assert error.details == {"test": "value"}

    error_without_details = ModelError("Test error")
    assert str(error_without_details) == "Test error"
    assert error_without_details.message == "Test error"
    assert error_without_details.code is None
    assert error_without_details.details == {} 