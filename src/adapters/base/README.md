# 基础适配器包

## 简介
基础适配器包提供了LLM适配器的核心接口和类型定义，是所有具体适配器实现的基础。

## 主要组件

### 1. 类型定义 (types.py)
- `ModelProvider`: 模型提供商枚举
- `ModelConfig`: 模型配置数据类
- `ModelResponse`: 模型响应数据类
- `ModelError`: 错误类定义

### 2. 接口定义 (interface.py)
- `BaseLLMAdapter`: LLM适配器抽象基类
  - 定义了标准的初始化流程
  - 提供了统一的接口规范
  - 包含基础的配置验证

## 使用说明

### 创建新的适配器
1. 继承 `BaseLLMAdapter` 类
2. 实现所有抽象方法
3. 根据需要扩展功能

示例：
```python
from adapters.base import BaseLLMAdapter, ModelConfig

class CustomAdapter(BaseLLMAdapter):
    def _setup(self) -> None:
        # 实现初始化逻辑
        pass

    async def chat_completion(self, messages, **kwargs):
        # 实现聊天补全
        pass

    async def completion(self, prompt, **kwargs):
        # 实现文本补全
        pass

    async def embeddings(self, texts, **kwargs):
        # 实现文本嵌入
        pass
```

### 配置管理
使用 `ModelConfig` 进行配置：
```python
config = ModelConfig(
    provider=ModelProvider.CUSTOM,
    model_name="custom-model",
    api_key="your-api-key"
)
```

## 错误处理
所有适配器相关的错误都应该使用 `ModelError` 或其子类：
```python
try:
    # 适配器操作
    pass
except Exception as e:
    raise ModelError(f"操作失败: {str(e)}")
```

## 注意事项
1. 所有适配器实现必须是异步的
2. 必须正确处理配置验证
3. 应该提供详细的错误信息
4. 建议实现重试机制 