"""Test cases for message routing"""
import pytest
from typing import List, Optional
from datetime import datetime

from src.core.comms.types import Message, MessageType, MessagePriority, MessageStatus
from src.core.comms.router import Route, Router, RouteHandler

class TestHandler(RouteHandler):
    """测试用的消息处理器"""
    def __init__(self):
        self.messages: List[Message] = []
        
    async def handle(self, message: Message) -> Optional[Message]:
        self.messages.append(message)
        return None

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

@pytest.fixture
def test_handler():
    """创建测试处理器"""
    return TestHandler()

@pytest.fixture
def router():
    """创建路由器"""
    return Router()

@pytest.mark.asyncio
async def test_route_creation():
    """测试路由创建"""
    handler = TestHandler()
    route = Route(
        pattern="test.*",
        handler=handler,
        priority=1
    )
    
    assert route.pattern == "test.*"
    assert route.handler == handler
    assert route.priority == 1

@pytest.mark.asyncio
async def test_router_add_route(router, test_handler):
    """测试添加路由"""
    router.add_route("test.*", test_handler)
    assert len(router.routes) == 1
    assert router.routes[0].pattern == "test.*"
    assert router.routes[0].handler == test_handler

@pytest.mark.asyncio
async def test_router_remove_route(router, test_handler):
    """测试移除路由"""
    router.add_route("test.*", test_handler)
    assert len(router.routes) == 1
    
    router.remove_route("test.*")
    assert len(router.routes) == 0

@pytest.mark.asyncio
async def test_router_get_handlers(router, test_handler):
    """测试获取处理器"""
    router.add_route("test.*", test_handler)
    
    handlers = router.get_handlers("test_receiver")
    assert len(handlers) == 1
    assert handlers[0] == test_handler
    
    handlers = router.get_handlers("other_receiver")
    assert len(handlers) == 0

@pytest.mark.asyncio
async def test_router_route_message(router, test_handler, test_message):
    """测试消息路由"""
    router.add_route("test.*", test_handler)
    
    # 路由消息
    await router.route(test_message)
    
    # 验证消息是否被处理
    assert len(test_handler.messages) == 1
    assert test_handler.messages[0] == test_message

@pytest.mark.asyncio
async def test_router_multiple_handlers(router, test_message):
    """测试多个处理器"""
    handler1 = TestHandler()
    handler2 = TestHandler()
    
    router.add_route("test.*", handler1, priority=1)
    router.add_route("test.*", handler2, priority=2)
    
    # 路由消息
    await router.route(test_message)
    
    # 验证消息是否按优先级顺序处理
    assert len(handler2.messages) == 1  # 高优先级处理器
    assert len(handler1.messages) == 1  # 低优先级处理器

@pytest.mark.asyncio
async def test_router_no_matching_handlers(router, test_message):
    """测试无匹配处理器"""
    handler = TestHandler()
    router.add_route("other.*", handler)
    
    # 路由消息
    await router.route(test_message)
    
    # 验证消息未被处理
    assert len(handler.messages) == 0

@pytest.mark.asyncio
async def test_router_pattern_matching(router, test_handler):
    """测试路由模式匹配"""
    router.add_route("test.*", test_handler)
    
    # 测试不同的接收者
    messages = [
        Message(
            id="1",
            type=MessageType.TASK,
            priority=MessagePriority.MEDIUM,
            sender="sender",
            receiver=receiver,
            content={},
            timestamp=datetime.utcnow(),
            trace_id="trace",
            timeout=60,
            status=MessageStatus.PENDING
        )
        for receiver in ["test_1", "test_2", "other"]
    ]
    
    # 路由所有消息
    for message in messages:
        await router.route(message)
    
    # 验证只有匹配的消息被处理
    assert len(test_handler.messages) == 2  # 只有test_1和test_2匹配 