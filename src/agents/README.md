# Agents 包

`agents` 包提供了一个智能代理系统，用于协调和执行复杂的任务。该系统包含多个专门的代理角色，每个角色都具有特定的职责和能力。

## 架构

```
agents/
├── base/           # 基础代理类和接口
│   ├── types.py   # 基本类型定义
│   └── interface.py # 代理接口定义
├── roles/          # 不同角色的代理实现
│   ├── coordinator.py    # 协调者代理
│   ├── product_manager.py # 产品经理代理
│   └── developer.py      # 开发者代理
└── utils/          # 工具函数和辅助模块
```

## 核心组件

### 基础代理 (BaseAgent)

所有代理的基类，定义了代理的基本接口和行为：

```python
class BaseAgent:
    """基础代理类"""
    
    async def process(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """处理输入消息并返回响应"""
        
    async def plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """规划任务的执行步骤"""
        
    async def execute(self, plan: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """执行具体任务"""
```

### 代理角色

1. 协调者 (Coordinator)
   - 任务分析和分配
   - 角色分配
   - 工作流创建
   - 进度监控

2. 产品经理 (ProductManager)
   - 需求分析
   - 规格说明创建
   - 用户故事生成
   - 产品计划制定
   - 开发初始化

3. 开发者 (Developer)
   - 代码分析
   - 解决方案实现
   - 测试执行
   - 代码审查

## 配置

### 代理配置

```python
from src.agents.base.types import AgentConfig, AgentRole

config = AgentConfig(
    role=AgentRole.DEVELOPER,     # 代理角色
    llm_config={                  # LLM配置
        "adapter": "openai",
        "model": "gpt-4",
        "api_key": "your-api-key"
    }
)
```

## 使用示例

### 使用协调者代理

```python
from src.agents.roles.coordinator import CoordinatorAgent
from src.agents.base.types import AgentConfig, AgentRole

async def coordinator_example():
    config = AgentConfig(
        role=AgentRole.COORDINATOR,
        llm_config={
            "adapter": "openai",
            "model": "gpt-4",
            "api_key": "your-api-key"
        }
    )
    
    agent = CoordinatorAgent(config)
    
    # 处理任务
    response = await agent.process(
        "我需要开发一个新功能，包括前端界面和后端API"
    )
    
    print(response.metadata)  # 输出任务分析和分配结果
```

### 使用产品经理代理

```python
from src.agents.roles.product_manager import ProductManagerAgent
from src.agents.base.types import AgentConfig, AgentRole

async def pm_example():
    config = AgentConfig(
        role=AgentRole.PRODUCT_MANAGER,
        llm_config={
            "adapter": "openai",
            "model": "gpt-4",
            "api_key": "your-api-key"
        }
    )
    
    agent = ProductManagerAgent(config)
    
    # 处理需求
    response = await agent.process(
        "设计一个用户注册功能"
    )
    
    print(response.metadata)  # 输出需求分析和规格说明
```

### 使用开发者代理

```python
from src.agents.roles.developer import DeveloperAgent
from src.agents.base.types import AgentConfig, AgentRole

async def dev_example():
    config = AgentConfig(
        role=AgentRole.DEVELOPER,
        llm_config={
            "adapter": "openai",
            "model": "gpt-4",
            "api_key": "your-api-key"
        }
    )
    
    agent = DeveloperAgent(config)
    
    # 处理开发任务
    response = await agent.process(
        "实现用户注册API"
    )
    
    print(response.metadata)  # 输出代码分析和实现结果
```

## 错误处理

```python
try:
    response = await agent.process("任务描述")
except ValueError as e:
    print(f"输入错误: {e}")
except Exception as e:
    print(f"处理错误: {e}")
```

## 扩展代理

要创建新的代理角色，继承 `BaseAgent` 类并实现必要的方法：

```python
from src.agents.base import BaseAgent
from typing import Dict, Optional, Any

class CustomAgent(BaseAgent):
    """自定义代理"""
    
    async def process(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        # 实现处理逻辑
        pass
    
    async def plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        # 实现规划逻辑
        pass
    
    async def execute(self, plan: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        # 实现执行逻辑
        pass
``` 