# 基础适配器 API 文档

## 类型定义

### ModelProvider
模型提供商枚举类。

```python
class ModelProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    ZHIPU = "zhipu"
    MOONSHOT = "moonshot"
    DEEPSEEK = "deepseek"
```

### ModelConfig
模型配置数据类。

```python
class ModelConfig(BaseModel):
    provider: ModelProvider      # 模型提供商
    model_name: str             # 模型名称
    api_key: str               # API密钥
    base_url: Optional[str]    # 可选的基础URL
    timeout: int = 60          # 超时时间（秒）
    max_retries: int = 3       # 最大重试次数
    temperature: float = 0.7   # 温度参数
    max_tokens: Optional[int]  # 最大token数
    extra_params: Dict[str, Any] = {} # 额外参数
```

### ModelResponse
模型响应数据类。

```python
class ModelResponse(BaseModel):
    content: str               # 响应内容
    role: str                 # 角色（如system/user/assistant）
    model: str               # 使用的模型
    usage: Dict[str, int]    # 使用统计
    raw_response: Dict[str, Any] # 原始响应
```

### ModelError
模型错误类。

```python
class ModelError(Exception):
    message: str              # 错误信息
    code: Optional[str]       # 错误代码
    details: Dict            # 详细信息
```

## 接口定义

### BaseLLMAdapter
LLM适配器基类。

#### 初始化
```python
def __init__(self, config: ModelConfig)
```
- 参数：
  - config: ModelConfig对象，包含适配器配置

#### 聊天补全
```python
async def chat_completion(
    self,
    messages: List[Dict[str, str]],
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    **kwargs
) -> ModelResponse
```
- 参数：
  - messages: 消息列表，每个消息包含role和content
  - temperature: 可选的温度参数
  - max_tokens: 可选的最大token数
  - kwargs: 其他参数
- 返回：
  - ModelResponse对象

#### 文本补全
```python
async def completion(
    self,
    prompt: str,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    **kwargs
) -> ModelResponse
```
- 参数：
  - prompt: 提示文本
  - temperature: 可选的温度参数
  - max_tokens: 可选的最大token数
  - kwargs: 其他参数
- 返回：
  - ModelResponse对象

#### 文本嵌入
```python
async def embeddings(
    self,
    texts: List[str],
    **kwargs
) -> List[List[float]]
```
- 参数：
  - texts: 待嵌入的文本列表
  - kwargs: 其他参数
- 返回：
  - 嵌入向量列表

## 使用示例

### 基本使用
```python
from adapters.base import BaseLLMAdapter, ModelConfig, ModelProvider

# 创建配置
config = ModelConfig(
    provider=ModelProvider.OPENAI,
    model_name="gpt-3.5-turbo",
    api_key="your-api-key"
)

# 创建适配器实例
adapter = YourAdapter(config)

# 使用聊天补全
response = await adapter.chat_completion([
    {"role": "user", "content": "Hello!"}
])

# 使用文本补全
response = await adapter.completion("Complete this: The sky is")

# 使用文本嵌入
embeddings = await adapter.embeddings(["Text to embed"])
```

### 错误处理
```python
try:
    response = await adapter.chat_completion(messages)
except ModelError as e:
    print(f"错误: {e.message}")
    if e.code:
        print(f"错误代码: {e.code}")
    if e.details:
        print(f"详细信息: {e.details}")
``` 