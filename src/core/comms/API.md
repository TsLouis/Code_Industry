# 通信系统 API 文档

## 1. 序列化器 API (Serialization)

### 1.1 JSON序列化器
```python
class JSONSerializer(BaseSerializer):
    def serialize(self, message: Message) -> str:
        """将消息序列化为JSON字符串"""
        pass

    def deserialize(self, data: str) -> Message:
        """将JSON字符串反序列化为消息对象"""
        pass
```

### 1.2 MessagePack序列化器
```python
class MessagePackSerializer(BaseSerializer):
    def serialize(self, message: Message) -> bytes:
        """将消息序列化为MessagePack格式"""
        pass

    def deserialize(self, data: bytes) -> Message:
        """将MessagePack数据反序列化为消息对象"""
        pass
```

## 2. 过滤器 API (Filters)

### 2.1 类型过滤器
```python
class TypeFilter(BaseFilter):
    def __init__(self, allowed_types: List[str]):
        """初始化类型过滤器"""
        self.allowed_types = allowed_types

    async def filter(self, message: Message) -> bool:
        """根据消息类型进行过滤"""
        pass
```

### 2.2 优先级过滤器
```python
class PriorityFilter(BaseFilter):
    def __init__(self, min_priority: int = 0):
        """初始化优先级过滤器"""
        self.min_priority = min_priority

    async def filter(self, message: Message) -> bool:
        """根据消息优先级进行过滤"""
        pass
```

### 2.3 组合过滤器
```python
class CompositeFilter(BaseFilter):
    def __init__(self, filters: List[BaseFilter], operator: str = "AND"):
        """初始化组合过滤器"""
        self.filters = filters
        self.operator = operator

    async def filter(self, message: Message) -> bool:
        """组合多个过滤器的结果"""
        pass
```

## 3. 路由器 API (Router)

### 3.1 基础路由器
```python
class Router:
    def register_route(self, pattern: str, handler: RouteHandler) -> None:
        """注册路由规则"""
        pass

    def remove_route(self, pattern: str) -> bool:
        """移除路由规则"""
        pass

    async def route(self, message: Message) -> None:
        """路由消息到对应的处理器"""
        pass
```

### 3.2 优先级路由器
```python
class PriorityRouter(Router):
    def register_route(self, pattern: str, handler: RouteHandler, priority: int = 0) -> None:
        """注册带优先级的路由规则"""
        pass

    async def route(self, message: Message) -> None:
        """按优先级顺序路由消息"""
        pass
```

## 4. 协议 API (Protocol)

### 4.1 消息处理器
```python
class MessageHandler:
    async def handle(self, message: Message) -> None:
        """处理消息的标准接口"""
        pass

    async def on_error(self, error: Exception, message: Message) -> None:
        """错误处理回调"""
        pass
```

### 4.2 重试策略
```python
class RetryStrategy:
    def __init__(self, max_retries: int = 3, delay: float = 1.0):
        """初始化重试策略"""
        self.max_retries = max_retries
        self.delay = delay

    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """执行带重试的操作"""
        pass
```

## 5. 消息代理 API (Broker)

### 5.1 基本操作
```python
class MessageBroker:
    async def publish(self, topic: str, message: Message) -> None:
        """发布消息到指定主题"""
        pass

    async def subscribe(self, topic: str, handler: MessageHandler) -> Subscription:
        """订阅指定主题"""
        pass

    async def unsubscribe(self, subscription: Subscription) -> None:
        """取消订阅"""
        pass
```

### 5.2 高级功能
```python
class MessageBroker:
    async def broadcast(self, message: Message) -> None:
        """广播消息到所有订阅者"""
        pass

    async def request(self, target: str, message: Message, timeout: float = 30.0) -> Message:
        """发送请求并等待响应"""
        pass

    async def reply(self, request: Message, response: Message) -> None:
        """回复特定请求"""
        pass
```

## 6. 类型定义

### 6.1 基本消息类型
```python
class Message:
    id: str
    type: str
    sender: str
    receiver: str
    content: Any
    priority: int = 0
    timestamp: datetime
    metadata: Dict[str, Any] = {}
```

### 6.2 订阅类型
```python
class Subscription:
    id: str
    topic: str
    handler: MessageHandler
    filters: List[BaseFilter] = []
```

## 7. 错误处理

### 7.1 异常类型
```python
class CommsError(Exception):
    """基础通信错误"""
    pass

class SerializationError(CommsError):
    """序列化错误"""
    pass

class RoutingError(CommsError):
    """路由错误"""
    pass

class FilterError(CommsError):
    """过滤器错误"""
    pass

class BrokerError(CommsError):
    """代理错误"""
    pass
```

### 7.2 错误码
```python
ERROR_CODES = {
    # 序列化错误
    "SERIALIZATION_ERROR": 1001,
    "DESERIALIZATION_ERROR": 1002,
    
    # 路由错误
    "ROUTE_NOT_FOUND": 2001,
    "HANDLER_ERROR": 2002,
    
    # 过滤器错误
    "FILTER_ERROR": 3001,
    
    # 代理错误
    "PUBLISH_ERROR": 4001,
    "SUBSCRIBE_ERROR": 4002,
    "TIMEOUT_ERROR": 4003
} 