"""
消息过滤器模块
"""

from typing import List, Optional, Dict, Any
from .types import Message
from ..monitoring.decorators import monitor_filter

class MessageFilter:
    """消息过滤器基类"""
    
    @monitor_filter("filter_check")
    async def filter(self, message: Message) -> bool:
        """过滤消息"""
        raise NotImplementedError

class TypeFilter(MessageFilter):
    """类型过滤器"""
    
    def __init__(self, allowed_types: List[str]):
        self.allowed_types = allowed_types
        
    @monitor_filter("type_filter")
    async def filter(self, message: Message) -> bool:
        """根据消息类型过滤"""
        return message.type in self.allowed_types

class PriorityFilter(MessageFilter):
    """优先级过滤器"""
    
    def __init__(self, min_priority: int = 0):
        self.min_priority = min_priority
        
    @monitor_filter("priority_filter")
    async def filter(self, message: Message) -> bool:
        """根据消息优先级过滤"""
        return message.priority >= self.min_priority

class SenderFilter(MessageFilter):
    """发送者过滤器"""
    
    def __init__(self, allowed_senders: List[str]):
        self.allowed_senders = allowed_senders
        
    @monitor_filter("sender_filter")
    async def filter(self, message: Message) -> bool:
        """根据发送者过滤"""
        return message.sender in self.allowed_senders

class ReceiverFilter(MessageFilter):
    """接收者过滤器"""
    
    def __init__(self, allowed_receivers: List[str]):
        self.allowed_receivers = allowed_receivers
        
    @monitor_filter("receiver_filter")
    async def filter(self, message: Message) -> bool:
        """根据接收者过滤"""
        return message.receiver in self.allowed_receivers

class CompositeFilter(MessageFilter):
    """组合过滤器"""
    
    def __init__(self, filters: List[MessageFilter], operator: str = "AND"):
        self.filters = filters
        self.operator = operator
        
    @monitor_filter("composite_filter")
    async def filter(self, message: Message) -> bool:
        """组合多个过滤器的结果"""
        if not self.filters:
            return True
            
        results = [await f.filter(message) for f in self.filters]
        
        if self.operator == "AND":
            return all(results)
        elif self.operator == "OR":
            return any(results)
        else:
            raise ValueError(f"Unknown operator: {self.operator}")

class ContentFilter(MessageFilter):
    """内容过滤器"""
    
    def __init__(self, required_fields: List[str], field_values: Optional[Dict[str, Any]] = None):
        self.required_fields = required_fields
        self.field_values = field_values or {}
        
    @monitor_filter("content_filter")
    async def filter(self, message: Message) -> bool:
        """根据消息内容过滤"""
        # 检查必需字段
        for field in self.required_fields:
            if field not in message.content:
                return False
                
        # 检查字段值
        for field, value in self.field_values.items():
            if field not in message.content or message.content[field] != value:
                return False
                
        return True 