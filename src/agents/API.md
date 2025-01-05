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
        role: AgentRole,           # 代理角色
        llm_config: Dict[str, Any],  # LLM配置
        name: Optional[str] = None,  # 代理名称
        description: Optional[str] = None,  # 代理描述
        instructions: Optional[str] = None,  # 代理指令
        tools: Optional[List[str]] = None,  # 可用工具
        metadata: Optional[Dict[str, Any]] = None  # 元数据
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
        name: Optional[str] = None  # 发送者名称
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
        metadata: Optional[Dict[str, Any]] = None,  # 元数据
        error: Optional[str] = None  # 错误信息
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
    
    async def process(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """处理输入消息
        
        Args:
            message: 输入消息
            context: 上下文信息
            
        Returns:
            AgentResponse: 代理响应
            
        Raises:
            ValueError: 当输入消息为空时
        """
        pass
    
    async def plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """规划任务
        
        Args:
            task: 任务描述
            context: 上下文信息
            
        Returns:
            AgentResponse: 规划结果
            
        Raises:
            ValueError: 当任务描述为空时
        """
        pass
    
    async def execute(self, plan: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """执行任务
        
        Args:
            plan: 执行计划
            context: 上下文信息
            
        Returns:
            AgentResponse: 执行结果
            
        Raises:
            ValueError: 当执行计划为空时
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
    
    async def process(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """处理协调请求"""
        pass
    
    async def _analyze_task(self, task: str) -> Dict[str, Any]:
        """分析任务"""
        pass
    
    async def _assign_roles(self, task_analysis: Dict[str, Any]) -> List[str]:
        """分配角色"""
        pass
    
    async def _create_workflow(self, role_assignments: List[str]) -> Dict[str, Any]:
        """创建工作流"""
        pass
    
    async def _monitor_progress(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """监控进度"""
        pass
```

### product_manager.py

#### ProductManagerAgent

产品经理代理：

```python
class ProductManagerAgent(BaseAgent):
    """产品经理代理"""
    
    async def process(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """处理产品需求"""
        pass
    
    async def _analyze_requirements(self, message: str) -> List[Requirement]:
        """分析需求"""
        pass
    
    async def _create_specifications(self, requirements: List[Requirement]) -> Specifications:
        """创建规格说明"""
        pass
    
    async def _generate_user_stories(self, specs: Specifications) -> List[UserStory]:
        """生成用户故事"""
        pass
    
    async def _create_product_plan(self, stories: List[UserStory]) -> Dict[str, Any]:
        """创建产品计划"""
        pass
    
    async def _initialize_development(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """初始化开发"""
        pass
```

### developer.py

#### DeveloperAgent

开发者代理：

```python
class DeveloperAgent(BaseAgent):
    """开发者代理"""
    
    async def process(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """处理开发任务"""
        pass
    
    async def _analyze_code(self, code: str) -> Dict[str, Any]:
        """分析代码"""
        pass
    
    async def _implement_solution(self, analysis: Dict[str, Any]) -> List[str]:
        """实现解决方案"""
        pass
    
    async def _test_implementation(self, implementation: List[str]) -> Dict[str, Any]:
        """测试实现"""
        pass
    
    async def _review_code(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        """代码审查"""
        pass
```

## 工具模块 (utils)

### llm.py

LLM 工具类：

```python
class LLMTool:
    """LLM 工具类"""
    
    def __init__(self, adapter: str):
        """初始化 LLM 工具
        
        Args:
            adapter: LLM 适配器名称
        """
        pass
    
    async def analyze_intent(self, message: str) -> Dict[str, Any]:
        """分析消息意图"""
        pass
    
    async def analyze_task_type(self, task: str) -> str:
        """分析任务类型"""
        pass
``` 