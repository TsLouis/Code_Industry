"""
Communication module type definitions
"""

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class MessageType(str, Enum):
    """消息类型"""
    TASK = "task"           # 任务消息
    STATUS = "status"       # 状态消息
    RESOURCE = "resource"   # 资源消息
    ERROR = "error"         # 错误消息


class MessageStatus(str, Enum):
    """消息状态"""
    PENDING = "pending"         # 等待处理
    PROCESSING = "processing"   # 处理中
    COMPLETED = "completed"     # 已完成
    FAILED = "failed"          # 失败


class MessagePriority(int, Enum):
    """消息优先级 1-5, 5最高"""
    LOWEST = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    HIGHEST = 5


class Message(BaseModel):
    """消息模型"""
    id: str = Field(..., description="消息唯一标识")
    type: MessageType = Field(..., description="消息类型")
    priority: MessagePriority = Field(MessagePriority.MEDIUM, description="消息优先级")
    sender: str = Field(..., description="发送者ID")
    receiver: str = Field(..., description="接收者ID")
    content: Dict[str, Any] = Field(default_factory=dict, description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")
    trace_id: str = Field(..., description="追踪ID")
    retry_count: int = Field(default=0, description="重试次数")
    timeout: int = Field(default=180, description="超时时间(秒)")
    status: MessageStatus = Field(default=MessageStatus.PENDING, description="消息状态")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")

    @field_validator("priority")
    def validate_priority(cls, v):
        if not isinstance(v, MessagePriority):
            raise ValueError(f"Invalid priority: {v}")
        return v

    @field_validator("timeout")
    def validate_timeout(cls, v):
        if v <= 0:
            raise ValueError("Timeout must be positive")
        return v

    @field_validator("retry_count")
    def validate_retry_count(cls, v):
        if v < 0:
            raise ValueError("Retry count cannot be negative")
        return v


class ErrorSeverity(str, Enum):
    """错误严重程度"""
    INFO = "info"           # 信息
    WARNING = "warning"     # 警告
    ERROR = "error"         # 错误
    CRITICAL = "critical"   # 严重


class Error(BaseModel):
    """错误模型"""
    code: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误消息")
    details: Optional[str] = Field(None, description="详细信息")
    severity: ErrorSeverity = Field(default=ErrorSeverity.ERROR, description="严重程度")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")


class RetryStrategy(BaseModel):
    """重试策略"""
    max_retries: int = Field(default=3, description="最大重试次数")
    base_delay: float = Field(default=1.0, description="基础延迟(秒)")
    max_delay: float = Field(default=60.0, description="最大延迟(秒)")
    multiplier: float = Field(default=2.0, description="延迟倍数")

    @field_validator("max_retries")
    def validate_max_retries(cls, v):
        if v < 0:
            raise ValueError("Max retries cannot be negative")
        return v

    @field_validator("base_delay", "max_delay")
    def validate_delay(cls, v):
        if v <= 0:
            raise ValueError("Delay must be positive")
        return v

    @field_validator("multiplier")
    def validate_multiplier(cls, v):
        if v <= 1:
            raise ValueError("Multiplier must be greater than 1")
        return v
        
    def get_delay(self, retry_count: int) -> float:
        """计算重试延迟时间
        
        Args:
            retry_count: 当前重试次数
            
        Returns:
            float: 延迟时间(秒)
        """
        delay = self.base_delay * (self.multiplier ** (retry_count - 1))
        return min(delay, self.max_delay)
        
    async def execute(self, operation: callable, timeout: Optional[float] = None) -> Any:
        """执行带重试的操作
        
        Args:
            operation: 要执行的操作
            timeout: 超时时间(秒)
            
        Returns:
            Any: 操作结果
            
        Raises:
            asyncio.TimeoutError: 操作超时
            MaxRetriesExceededError: 超过最大重试次数
            ProtocolError: 其他协议错误
        """
        from .protocol import RetryableError, MaxRetriesExceededError, ProtocolError
        import asyncio
        
        retry_count = 0
        last_error = None
        
        while retry_count <= self.max_retries:
            try:
                if timeout:
                    return await asyncio.wait_for(operation(), timeout)
                return await operation()
                
            except asyncio.TimeoutError:
                raise  # 直接重新抛出 asyncio.TimeoutError
                
            except RetryableError as e:
                last_error = e
                retry_count += 1
                if retry_count > self.max_retries:
                    break
                    
                delay = self.get_delay(retry_count)
                await asyncio.sleep(delay)
                continue
                
            except Exception as e:
                raise ProtocolError(f"Unexpected error: {str(e)}")
                
        raise MaxRetriesExceededError(
            f"Max retries exceeded ({self.max_retries}), "
            f"last error: {str(last_error)}"
        ) 