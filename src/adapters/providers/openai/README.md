# OpenAI适配器

## 简介
OpenAI适配器提供了与OpenAI API的标准化接口，支持GPT-3.5、GPT-4等模型的调用。

## 功能特点
1. 支持异步调用
2. 完整的错误处理
3. 自动重试机制
4. 灵活的配置选项

## 主要组件

### 1. 适配器实现 (client.py)
- `OpenAIAdapter`: OpenAI API的具体实现
  - 支持聊天补全
  - 支持文本补全
  - 支持文本嵌入

### 2. 配置管理 (config.py)
- `DEFAULT_MODELS`: 预定义模型配置
- `create_openai_config`: 配置创建函数

## 使用说明

### 基本配置
```python
from adapters.providers.openai import create_openai_config, OpenAIAdapter

# 创建配置
config = create_openai_config(
    api_key="your-api-key",
    model_name="gpt-3.5-turbo"
)

# 创建适配器实例
adapter = OpenAIAdapter(config)
```

### 聊天补全示例
```python
messages = [
    {"role": "system", "content": "你是一个有帮助的助手。"},
    {"role": "user", "content": "你好！"}
]

response = await adapter.chat_completion(messages)
print(response.content)
```

### 文本补全示例
```python
response = await adapter.completion(
    prompt="完成这个句子：人工智能的未来是",
    max_tokens=50
)
print(response.content)
```

### 文本嵌入示例
```python
texts = ["这是第一个句子", "这是第二个句子"]
embeddings = await adapter.embeddings(texts)
```

## 配置选项

### 模型配置
- gpt-3.5-turbo
  - max_tokens: 4096
  - temperature: 0.7
- gpt-4
  - max_tokens: 8192
  - temperature: 0.7
- text-embedding-ada-002
  - 用于文本嵌入

### 自定义选项
```python
config = create_openai_config(
    api_key="your-api-key",
    model_name="gpt-3.5-turbo",
    base_url="your-custom-url",  # 自定义API地址
    timeout=30,                  # 自定义超时时间
    max_retries=5               # 自定义重试次数
)
```

## 错误处理
```python
try:
    response = await adapter.chat_completion(messages)
except ModelError as e:
    print(f"API调用失败: {e.message}")
    # 进行错误处理
```

## 注意事项
1. 请确保设置了正确的API密钥
2. 注意API调用的费用控制
3. 合理设置超时和重试参数
4. 建议在生产环境中使用异常处理 