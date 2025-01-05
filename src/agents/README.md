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
    
    async def process(self, message: str) -> AgentResponse:
        """处理输入消息并返回响应"""
        
    async def plan(self, task: str) -> List[Task]:
        """规划任务的执行步骤"""
        
    async def execute(self, task: Task) -> ExecutionResult:
        """执行具体任务"""
```

### 代理角色

1. 协调者 (Coordinator)
   - 负责任务分解和分配
   - 管理任务优先级
   - 协调多个代理之间的合作

2. 产品经理 (ProductManager)
   - 分析和管理需求
   - 创建产品规格说明
   - 生成用户故事
   - 跟踪开发进度

3. 开发者 (Developer)
   - 分析技术需求
   - 创建技术设计
   - 实现代码更改
   - 执行测试

## 配置

### 代理配置

```python
from code_industry.agents import AgentConfig

config = AgentConfig(
    role="developer",           # 代理角色
    name="DevAgent",           # 代理名称
    model_config={             # 模型配置
        "adapter": "openai",
        "model": "gpt-3.5-turbo"
    }
)
```

## 使用示例

### 使用协调者代理

```python
from code_industry.agents import CoordinatorAgent
from code_industry.agents.base import AgentConfig

async def coordinator_example():
    config = AgentConfig(
        role="coordinator",
        model_config={
            "adapter": "openai",
            "model": "gpt-3.5-turbo"
        }
    )
    
    agent = CoordinatorAgent(config)
    
    # 处理复杂任务
    response = await agent.process(
        "我需要开发一个电子商务网站，包括用户认证、商品管理和订单系统。"
    )
    
    print(response.tasks)  # 输出分解后的任务列表
```

### 使用产品经理代理

```python
from code_industry.agents import ProductManagerAgent

async def pm_example():
    config = AgentConfig(role="product_manager")
    agent = ProductManagerAgent(config)
    
    # 分析需求
    response = await agent.process(
        "设计一个移动应用的用户注册流程"
    )
    
    print(response.specifications)  # 输出产品规格
```

### 使用开发者代理

```python
from code_industry.agents import DeveloperAgent

async def dev_example():
    config = AgentConfig(role="developer")
    agent = DeveloperAgent(config)
    
    # 处理技术任务
    response = await agent.process(
        "实现用户认证系统的后端 API"
    )
    
    print(response.technical_design)  # 输出技术设计
```

## 错误处理

```python
from code_industry.agents.base import AgentError

try:
    response = await agent.process("任务描述")
except AgentError as e:
    print(f"代理错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")
```

## 扩展代理

要创建新的代理角色，继承 `BaseAgent` 类并实现必要的方法：

```python
from code_industry.agents.base import BaseAgent

class CustomAgent(BaseAgent):
    """自定义代理"""
    
    async def process(self, message: str) -> AgentResponse:
        # 实现处理逻辑
        pass
    
    async def plan(self, task: str) -> List[Task]:
        # 实现规划逻辑
        pass
    
    async def execute(self, task: Task) -> ExecutionResult:
        # 实现执行逻辑
        pass
``` 