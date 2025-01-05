import pytest
from typing import List, Dict
from src.adapters.base import BaseLLMAdapter, ModelConfig, ModelResponse, ModelProvider

class MockAdapter(BaseLLMAdapter):
    """用于测试的模拟适配器"""
    def __init__(self, config: ModelConfig, should_fail: bool = False):
        self.should_fail = should_fail
        super().__init__(config)

    def _setup(self) -> None:
        if self.should_fail:
            raise Exception("模拟设置失败")
        self.is_setup = True

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> ModelResponse:
        if self.should_fail:
            raise Exception("模拟聊天补全失败")
        return ModelResponse(
            content="模拟回复",
            role="assistant",
            model=self.config.model_name,
            usage={"prompt_tokens": 10, "completion_tokens": 20},
            raw_response={"choices": [{"message": {"content": "模拟回复"}}]}
        )

    async def completion(
        self,
        prompt: str,
        temperature: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> ModelResponse:
        if self.should_fail:
            raise Exception("模拟文本补全失败")
        return ModelResponse(
            content="模拟补全",
            role="assistant",
            model=self.config.model_name,
            usage={"prompt_tokens": 5, "completion_tokens": 10},
            raw_response={"choices": [{"text": "模拟补全"}]}
        )

    async def embeddings(
        self,
        texts: List[str],
        **kwargs
    ) -> List[List[float]]:
        if self.should_fail:
            raise Exception("模拟嵌入失败")
        return [[0.1, 0.2, 0.3] for _ in texts]

@pytest.fixture
def config():
    """创建测试配置"""
    return ModelConfig(
        provider=ModelProvider.OPENAI,
        model_name="test-model",
        api_key="test-key"
    )

@pytest.mark.asyncio
async def test_adapter_initialization(config):
    """测试适配器初始化"""
    # 测试正常初始化
    adapter = MockAdapter(config)
    assert adapter.config == config
    assert adapter.is_setup

    # 测试初始化失败
    with pytest.raises(Exception, match="模拟设置失败"):
        MockAdapter(config, should_fail=True)

@pytest.mark.asyncio
async def test_chat_completion(config):
    """测试聊天补全功能"""
    adapter = MockAdapter(config)
    messages = [
        {"role": "user", "content": "你好"}
    ]

    # 测试正常调用
    response = await adapter.chat_completion(messages)
    assert response.content == "模拟回复"
    assert response.role == "assistant"
    assert response.model == "test-model"

    # 测试调用失败
    adapter.should_fail = True
    with pytest.raises(Exception, match="模拟聊天补全失败"):
        await adapter.chat_completion(messages)

@pytest.mark.asyncio
async def test_completion(config):
    """测试文本补全功能"""
    adapter = MockAdapter(config)
    prompt = "完成这个句子："

    # 测试正常调用
    response = await adapter.completion(prompt)
    assert response.content == "模拟补全"
    assert response.role == "assistant"
    assert response.model == "test-model"

    # 测试调用失败
    adapter.should_fail = True
    with pytest.raises(Exception, match="模拟文本补全失败"):
        await adapter.completion(prompt)

@pytest.mark.asyncio
async def test_embeddings(config):
    """测试文本嵌入功能"""
    adapter = MockAdapter(config)
    texts = ["测试文本1", "测试文本2"]

    # 测试正常调用
    embeddings = await adapter.embeddings(texts)
    assert len(embeddings) == len(texts)
    assert all(len(embedding) == 3 for embedding in embeddings)
    assert all(isinstance(value, float) for embedding in embeddings for value in embedding)

    # 测试调用失败
    adapter.should_fail = True
    with pytest.raises(Exception, match="模拟嵌入失败"):
        await adapter.embeddings(texts) 