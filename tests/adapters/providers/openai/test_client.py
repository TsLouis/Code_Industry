import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from openai import AsyncOpenAI
from src.adapters.base.types import ModelConfig, ModelProvider, ModelError
from src.adapters.providers.openai import OpenAIAdapter

@pytest.fixture
def config():
    return ModelConfig(
        provider=ModelProvider.OPENAI,
        model_name="gpt-3.5-turbo",
        api_key="test-key"
    )

@pytest.fixture
def mock_openai():
    mock = AsyncMock(spec=AsyncOpenAI)
    
    # 设置chat属性
    mock.chat = AsyncMock()
    mock.chat.completions = AsyncMock()
    mock.chat.completions.create = AsyncMock()
    
    # 设置completions属性
    mock.completions = AsyncMock()
    mock.completions.create = AsyncMock()
    
    # 设置embeddings属性
    mock.embeddings = AsyncMock()
    mock.embeddings.create = AsyncMock()
    
    return mock

@pytest.mark.asyncio
async def test_chat_completion(config, mock_openai):
    """测试聊天补全功能"""
    mock_response = AsyncMock()
    mock_response.choices = [
        AsyncMock(
            message=AsyncMock(
                content="模拟回复",
                role="assistant"
            )
        )
    ]
    mock_response.model = "gpt-3.5-turbo"
    mock_response.usage = AsyncMock(
        model_dump=lambda: {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    )
    mock_response.model_dump = lambda: {"choices": [{"message": {"content": "模拟回复"}}]}

    adapter = OpenAIAdapter(config)
    adapter._client = mock_openai
    mock_openai.chat.completions.create.return_value = mock_response
    
    messages = [{"role": "user", "content": "你好"}]
    response = await adapter.chat_completion(messages)
    
    assert response.content == "模拟回复"
    assert response.role == "assistant"
    assert response.model == "gpt-3.5-turbo"
    assert response.usage["total_tokens"] == 30

@pytest.mark.asyncio
async def test_completion(config, mock_openai):
    """测试文本补全功能"""
    mock_response = AsyncMock()
    mock_response.choices = [AsyncMock(text="模拟补全")]
    mock_response.model = "gpt-3.5-turbo"
    mock_response.usage = AsyncMock(
        model_dump=lambda: {
            "prompt_tokens": 5,
            "completion_tokens": 10,
            "total_tokens": 15
        }
    )
    mock_response.model_dump = lambda: {"choices": [{"text": "模拟补全"}]}

    adapter = OpenAIAdapter(config)
    adapter._client = mock_openai
    mock_openai.completions.create.return_value = mock_response
    
    response = await adapter.completion("完成这个句子：")
    
    assert response.content == "模拟补全"
    assert response.role == "assistant"
    assert response.model == "gpt-3.5-turbo"
    assert response.usage["total_tokens"] == 15

@pytest.mark.asyncio
async def test_embeddings(config, mock_openai):
    """测试文本嵌入功能"""
    mock_response = AsyncMock()
    mock_response.data = [
        AsyncMock(embedding=[0.1, 0.2, 0.3]),
        AsyncMock(embedding=[0.4, 0.5, 0.6])
    ]

    adapter = OpenAIAdapter(config)
    adapter._client = mock_openai
    mock_openai.embeddings.create.return_value = mock_response
    
    texts = ["测试文本1", "测试文本2"]
    embeddings = await adapter.embeddings(texts)
    
    assert len(embeddings) == 2
    assert embeddings[0] == [0.1, 0.2, 0.3]
    assert embeddings[1] == [0.4, 0.5, 0.6]

@pytest.mark.asyncio
async def test_retry_mechanism(config, mock_openai):
    """测试重试机制"""
    mock_success = AsyncMock()
    mock_success.choices = [
        AsyncMock(
            message=AsyncMock(
                content="成功响应",
                role="assistant"
            )
        )
    ]
    mock_success.model = "gpt-3.5-turbo"
    mock_success.usage = AsyncMock(
        model_dump=lambda: {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    )
    mock_success.model_dump = lambda: {"choices": [{"message": {"content": "成功响应"}}]}

    adapter = OpenAIAdapter(config)
    adapter._client = mock_openai
    mock_openai.chat.completions.create.side_effect = [
        Exception("API错误"),
        Exception("API错误"),
        mock_success
    ]
    
    messages = [{"role": "user", "content": "测试"}]
    response = await adapter.chat_completion(messages)
    
    assert response.content == "成功响应"
    assert mock_openai.chat.completions.create.call_count == 3

@pytest.mark.asyncio
async def test_timeout_handling(config, mock_openai):
    """测试超时处理"""
    config.timeout = 1

    adapter = OpenAIAdapter(config)
    adapter._client = mock_openai
    mock_openai.chat.completions.create.side_effect = TimeoutError("请求超时")
    
    messages = [{"role": "user", "content": "测试"}]
    
    with pytest.raises(ModelError) as exc_info:
        await adapter.chat_completion(messages)
    assert "请求超时" in str(exc_info.value) 