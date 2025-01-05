# Agents API 文档

## 基础模块 (base)

### types.py

#### AgentRole

代理角色枚举类型：

```python
class AgentRole(str, Enum):
    """代理角色类型"""
    COORDINATOR = "coordinator"      # 协调者
    PRODUCT_MANAGER = "product_manager"  # 产品经理
    DEVELOPER = "developer"         # 开发者
    SYSTEM = "system"              # 系统
    USER = "user"                  # 用户
```

#### AgentConfig

代理配置类：

```python
class AgentConfig:
    """代理配置"""
    
    def __init__(
        self,
        role: str,                 # 代理角色
        name: Optional[str] = None,  # 代理名称
        model_config: Optional[Dict] = None  # 模型配置
    ):
        pass
```

#### Message

消息类型：

```python
class Message:
    """消息类型"""
    
    def __init__(
        self,
        role: AgentRole,           # 发送者角色
        content: str,              # 消息内容
        metadata: Optional[Dict] = None  # 元数据
    ):
        pass
```

#### AgentResponse

代理响应类型：

```python
class AgentResponse:
    """代理响应"""
    
    def __init__(
        self,
        response: str,             # 响应内容
        status: str,               # 状态
        metadata: Optional[Dict] = None  # 元数据
    ):
        pass
```

### interface.py

#### BaseAgent

基础代理接口：

```python
class BaseAgent:
    """基础代理类"""
    
    def __init__(self, config: AgentConfig):
        """初始化代理
        
        Args:
            config: 代理配置
        """
        pass
    
    async def process(self, message: str) -> AgentResponse:
        """处理输入消息
        
        Args:
            message: 输入消息
            
        Returns:
            AgentResponse: 代理响应
        """
        pass
    
    async def plan(self, task: str) -> List[Task]:
        """规划任务
        
        Args:
            task: 任务描述
            
        Returns:
            List[Task]: 任务列表
        """
        pass
    
    async def execute(self, task: Task) -> ExecutionResult:
        """执行任务
        
        Args:
            task: 要执行的任务
            
        Returns:
            ExecutionResult: 执行结果
        """
        pass
```

## 角色模块 (roles)

### coordinator.py

#### CoordinatorAgent

协调者代理：

```python
class CoordinatorAgent(BaseAgent):
    """协调者代理"""
    
    async def process(self, message: str) -> AgentResponse:
        """处理协调请求"""
        pass
    
    async def _decompose_task(self, task: str) -> List[Task]:
        """分解任务"""
        pass
    
    async def _calculate_priority(self, task: Task) -> int:
        """计算任务优先级"""
        pass
    
    async def _identify_dependencies(self, tasks: List[Task]) -> Dict[str, List[str]]:
        """识别任务依赖"""
        pass
    
    async def _estimate_time(self, task: Task) -> int:
        """估算任务时间"""
        pass
```

### product_manager.py

#### ProductManagerAgent

产品经理代理：

```python
class ProductManagerAgent(BaseAgent):
    """产品经理代理"""
    
    async def process(self, message: str) -> AgentResponse:
        """处理产品需求"""
        pass
    
    async def _analyze_requirements(self, requirements: str) -> List[Requirement]:
        """分析需求"""
        pass
    
    async def _create_specifications(self, requirements: List[Requirement]) -> Specifications:
        """创建规格说明"""
        pass
    
    async def _generate_user_stories(self, specifications: Specifications) -> List[UserStory]:
        """生成用户故事"""
        pass
```

### developer.py

#### DeveloperAgent

开发者代理：

```python
class DeveloperAgent(BaseAgent):
    """开发者代理"""
    
    async def process(self, message: str) -> AgentResponse:
        """处理开发任务"""
        pass
    
    async def _analyze_technical_requirements(self, requirements: str) -> List[TechnicalRequirement]:
        """分析技术需求"""
        pass
    
    async def _create_technical_design(self, requirements: List[TechnicalRequirement]) -> TechnicalDesign:
        """创建技术设计"""
        pass
    
    async def _plan_implementation(self, design: TechnicalDesign) -> List[ImplementationStep]:
        """规划实现步骤"""
        pass
    
    async def _implement_changes(self, steps: List[ImplementationStep]) -> List[CodeChange]:
        """实现代码更改"""
        pass
```

## 工具模块 (utils)

### llm.py

LLM 工具函数：

```python
async def generate_response(prompt: str, config: Dict) -> str:
    """生成 LLM 响应
    
    Args:
        prompt: 提示文本
        config: LLM 配置
        
    Returns:
        str: 生成的响应
    """
    pass

async def analyze_intent(message: str) -> Dict:
    """分析消息意图
    
    Args:
        message: 输入消息
        
    Returns:
        Dict: 意图分析结果
    """
    pass

async def calculate_priority(task: str) -> Dict:
    """计算任务优先级
    
    Args:
        task: 任务描述
        
    Returns:
        Dict: 优先级分析结果
    """
    pass
```

## 异常类型

### AgentError

代理错误基类：

```python
class AgentError(Exception):
    """代理错误基类"""
    pass

class ConfigurationError(AgentError):
    """配置错误"""
    pass

class ProcessingError(AgentError):
    """处理错误"""
    pass

class ExecutionError(AgentError):
    """执行错误"""
    pass
``` 