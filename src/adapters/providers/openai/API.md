# OpenAI适配器 API 文档

## 配置函数

### create_openai_config
创建OpenAI配置对象。

```python
def create_openai_config(
    api_key: str,
    model_name: str = "gpt-3.5-turbo",
    base_url: str = None,
    **kwargs
) -> ModelConfig
```

#### 参数
- api_key: OpenAI API密钥
- model_name: 模型名称，默认为"gpt-3.5-turbo"
- base_url: 可选的API基础URL
- kwargs: 其他配置参数
  - timeout: 超时时间（秒）
  - max_retries: 最大重试次数
  - temperature: 温度参数
  - max_tokens: 最大token数

#### 返回
- ModelConfig对象

#### 示例
```python
config = create_openai_config(
    api_key="your-api-key",
    model_name="gpt-4",
    temperature=0.8,
    max_tokens=2000
)
```

## OpenAIAdapter类

### 初始化
```python
adapter = OpenAIAdapter(config: ModelConfig)
```

### 方法

#### chat_completion
执行聊天补全。

```python
async def chat_completion(
    self,
    messages: List[Dict[str, str]],
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    **kwargs
) -> ModelResponse
```

##### 参数
- messages: 消息列表，每个消息包含role和content
- temperature: 可选的温度参数
- max_tokens: 可选的最大token数
- kwargs: 其他OpenAI API参数

##### 返回
- ModelResponse对象

##### 示例
```python
response = await adapter.chat_completion([
    {"role": "system", "content": "你是一个有帮助的助手。"},
    {"role": "user", "content": "请介绍一下Python。"}
])
```

#### completion
执行文本补全。

```python
async def completion(
    self,
    prompt: str,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    **kwargs
) -> ModelResponse
```

##### 参数
- prompt: 提示文本
- temperature: 可选的温度参数
- max_tokens: 可选的最大token数
- kwargs: 其他OpenAI API参数

##### 返回
- ModelResponse对象

##### 示例
```python
response = await adapter.completion(
    prompt="Python是一种",
    max_tokens=100
)
```

#### embeddings
生成文本嵌入。

```python
async def embeddings(
    self,
    texts: List[str],
    **kwargs
) -> List[List[float]]
```

##### 参数
- texts: 待嵌入的文本列表
- kwargs: 其他OpenAI API参数

##### 返回
- 嵌入向量列表

##### 示例
```python
embeddings = await adapter.embeddings([
    "第一个句子",
    "第二个句子"
])
```

## 预定义常量

### DEFAULT_MODELS
预定义的模型配置。

```python
DEFAULT_MODELS = {
    "gpt-3.5-turbo": {
        "max_tokens": 4096,
        "temperature": 0.7,
    },
    "gpt-4": {
        "max_tokens": 8192,
        "temperature": 0.7,
    },
    "text-embedding-ada-002": {
        "max_tokens": None,
        "temperature": None,
    }
}
```

## 错误处理

所有API调用都可能抛出ModelError异常：

```python
try:
    response = await adapter.chat_completion(messages)
except ModelError as e:
    print(f"错误信息: {e.message}")
    print(f"错误代码: {e.code}")
    print(f"详细信息: {e.details}")
```

## 类型提示

```python
from typing import Dict, List, Optional
from adapters.base import ModelConfig, ModelResponse, ModelError

# 消息格式
Message = Dict[str, str]  # {"role": str, "content": str}

# 嵌入向量
Embedding = List[float]
``` 