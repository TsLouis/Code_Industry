"""Test cases for message filters"""
import pytest
from datetime import datetime

from src.core.comms.types import Message, MessageType, MessagePriority, MessageStatus
from src.core.comms.filters import (
    MessageFilter,
    TypeFilter,
    PriorityFilter,
    SenderFilter,
    ReceiverFilter,
    CompositeFilter,
    FilterOperator
)

@pytest.fixture
def test_message():
    """创建测试消息"""
    return Message(
        id="test_id",
        type=MessageType.TASK,
        priority=MessagePriority.MEDIUM,
        sender="test_sender",
        receiver="test_receiver",
        content={"test": "value"},
        timestamp=datetime.utcnow(),
        trace_id="test_trace",
        timeout=60,
        status=MessageStatus.PENDING
    )

def test_type_filter(test_message):
    """测试类型过滤器"""
    # 测试匹配的类型
    filter = TypeFilter([MessageType.TASK])
    assert filter.matches(test_message) is True
    
    # 测试不匹配的类型
    filter = TypeFilter([MessageType.ERROR])
    assert filter.matches(test_message) is False
    
    # 测试多个类型
    filter = TypeFilter([MessageType.TASK, MessageType.ERROR])
    assert filter.matches(test_message) is True

def test_priority_filter(test_message):
    """测试优先级过滤器"""
    # 测试匹配的优先级
    filter = PriorityFilter([MessagePriority.MEDIUM])
    assert filter.matches(test_message) is True
    
    # 测试不匹配的优先级
    filter = PriorityFilter([MessagePriority.HIGH])
    assert filter.matches(test_message) is False
    
    # 测试多个优先级
    filter = PriorityFilter([MessagePriority.HIGH, MessagePriority.MEDIUM])
    assert filter.matches(test_message) is True

def test_sender_filter(test_message):
    """测试发送者过滤器"""
    # 测试匹配的发送者
    filter = SenderFilter(["test_sender"])
    assert filter.matches(test_message) is True
    
    # 测试不匹配的发送者
    filter = SenderFilter(["other_sender"])
    assert filter.matches(test_message) is False
    
    # 测试正则表达式匹配
    filter = SenderFilter(["test.*"])
    assert filter.matches(test_message) is True

def test_receiver_filter(test_message):
    """测试接收者过滤器"""
    # 测试匹配的接收者
    filter = ReceiverFilter(["test_receiver"])
    assert filter.matches(test_message) is True
    
    # 测试不匹配的接收者
    filter = ReceiverFilter(["other_receiver"])
    assert filter.matches(test_message) is False
    
    # 测试正则表达式匹配
    filter = ReceiverFilter(["test.*"])
    assert filter.matches(test_message) is True

def test_composite_filter_and(test_message):
    """测试组合过滤器 AND 操作"""
    type_filter = TypeFilter([MessageType.TASK])
    priority_filter = PriorityFilter([MessagePriority.MEDIUM])
    
    # 测试两个匹配的过滤器
    filter = CompositeFilter([type_filter, priority_filter], FilterOperator.AND)
    assert filter.matches(test_message) is True
    
    # 测试一个匹配一个不匹配的过滤器
    priority_filter = PriorityFilter([MessagePriority.HIGH])
    filter = CompositeFilter([type_filter, priority_filter], FilterOperator.AND)
    assert filter.matches(test_message) is False

def test_composite_filter_or(test_message):
    """测试组合过滤器 OR 操作"""
    type_filter = TypeFilter([MessageType.ERROR])
    priority_filter = PriorityFilter([MessagePriority.MEDIUM])
    
    # 测试一个匹配一个不匹配的过滤器
    filter = CompositeFilter([type_filter, priority_filter], FilterOperator.OR)
    assert filter.matches(test_message) is True
    
    # 测试两个不匹配的过滤器
    priority_filter = PriorityFilter([MessagePriority.HIGH])
    filter = CompositeFilter([type_filter, priority_filter], FilterOperator.OR)
    assert filter.matches(test_message) is False

def test_composite_filter_nested(test_message):
    """测试嵌套组合过滤器"""
    type_filter = TypeFilter([MessageType.TASK])
    priority_filter = PriorityFilter([MessagePriority.MEDIUM])
    sender_filter = SenderFilter(["test_sender"])
    receiver_filter = ReceiverFilter(["other_receiver"])
    
    # 创建嵌套的组合过滤器
    inner_filter = CompositeFilter([type_filter, priority_filter], FilterOperator.AND)
    outer_filter = CompositeFilter([inner_filter, sender_filter], FilterOperator.AND)
    
    # 测试全部匹配
    assert outer_filter.matches(test_message) is True
    
    # 测试部分匹配
    outer_filter = CompositeFilter([inner_filter, receiver_filter], FilterOperator.AND)
    assert outer_filter.matches(test_message) is False

def test_filter_chain(test_message):
    """测试过滤器链"""
    filters = [
        TypeFilter([MessageType.TASK]),
        PriorityFilter([MessagePriority.MEDIUM]),
        SenderFilter(["test_sender"]),
        ReceiverFilter(["test_receiver"])
    ]
    
    # 测试过滤器链全部匹配
    for filter in filters:
        assert filter.matches(test_message) is True
    
    # 修改一个过滤器使其不匹配
    filters[1] = PriorityFilter([MessagePriority.HIGH])
    assert filters[1].matches(test_message) is False 