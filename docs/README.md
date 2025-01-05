# Code Industry

Code Industry 是一个现代化的 LLM 适配器框架，提供了统一的接口来集成和使用不同的大语言模型。

## 特性

- 统一的适配器接口
- 多种 LLM 提供者支持
- 智能代理系统
- 完整的类型提示
- 异步操作支持
- 全面的错误处理
- 详细的文档

## 安装

```bash
pip install code-industry
```

## 快速开始

1. 设置环境变量：

```bash
export OPENAI_API_KEY=your_api_key_here
```

2. 创建适配器：

```python
from code_industry.adapters import OpenAIAdapter
from code_industry.base import ModelConfig

config = ModelConfig(
    provider="openai",
    model="gpt-3.5-turbo",
    api_key="your_api_key_here"
)

adapter = OpenAIAdapter(config)
```

3. 使用适配器：

```python
async def main():
    response = await adapter.generate("你好，请介绍一下你自己。")
    print(response.content)

asyncio.run(main())
```

## 项目结构

```
code_industry/
├── src/
│   ├── adapters/          # LLM 适配器实现
│   │   ├── base/         # 基础接口和类型
│   │   └── providers/    # 不同提供者的适配器
│   ├── agents/           # 智能代理实现
│   │   ├── base/        # 基础代理类
│   │   └── roles/       # 不同角色的代理
│   └── utils/            # 工具函数
├── tests/                # 测试用例
├── docs/                 # 文档
└── examples/            # 示例代码
```

## 开发指南

1. 克隆仓库：

```bash
git clone https://github.com/your-username/code-industry.git
cd code-industry
```

2. 创建虚拟环境：

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. 安装依赖：

```bash
pip install -e ".[dev]"
```

4. 运行测试：

```bash
pytest
```

## 使用示例

### 使用 OpenAI 适配器

```python
from code_industry.adapters import OpenAIAdapter
from code_industry.base import ModelConfig

async def chat_example():
    config = ModelConfig(
        provider="openai",
        model="gpt-3.5-turbo",
        temperature=0.7
    )
    
    adapter = OpenAIAdapter(config)
    
    response = await adapter.generate(
        "请用简单的话解释什么是机器学习。"
    )
    
    print(response.content)
```

### 使用开发者代理

```python
from code_industry.agents import DeveloperAgent
from code_industry.base import AgentConfig

async def developer_example():
    config = AgentConfig(
        model_config={
            "adapter": "openai",
            "model": "gpt-3.5-turbo"
        }
    )
    
    agent = DeveloperAgent(config)
    
    response = await agent.process(
        "我需要一个用户认证系统的技术方案。"
    )
    
    print(response.response)
```

## 配置说明

### 模型配置

```python
ModelConfig(
    provider="openai",           # LLM 提供者
    model="gpt-3.5-turbo",      # 模型名称
    temperature=0.7,            # 温度参数
    max_tokens=2000,            # 最大标记数
    api_key="your_api_key"      # API密钥
)
```

### 代理配置

```python
AgentConfig(
    model_config={              # 模型配置
        "adapter": "openai",
        "model": "gpt-3.5-turbo"
    },
    role="developer",           # 代理角色
    name="DevAgent"            # 代理名称
)
```

## 错误处理

```python
from code_industry.base import ModelError

try:
    response = await adapter.generate("你好")
except ModelError as e:
    print(f"模型错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")
```

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License 