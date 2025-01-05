"""Test cases for message protocol"""
import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Optional

from src.core.comms.types import Message, MessageType, MessagePriority, MessageStatus
from src.core.comms.protocol import (
    MessageHandler,
    RetryStrategy,
    RetryableError,
    MaxRetriesExceededError
)

class TestHandler(MessageHandler):
    """测试用的消息处理器"""
    def __init__(self, should_fail: bool = False, delay: float = 0):
        self.should_fail = should_fail
        self.delay = delay
        self.handled_messages = []
        self.error_count = 0
        
    async def handle(self, message: Message) -> Optional[Message]:
        if self.delay > 0:
            await asyncio.sleep(self.delay)
            
        if self.should_fail:
            self.error_count += 1
            raise RetryableError("Handler failed")
            
        self.handled_messages.append(message)
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
def retry_strategy():
    """创建重试策略"""
    return RetryStrategy(
        max_retries=3,
        base_delay=0.1,
        max_delay=1.0,
        multiplier=2.0
    )

@pytest.mark.asyncio
async def test_handler_success(test_message):
    """测试处理器成功处理消息"""
    handler = TestHandler()
    await handler.handle(test_message)
    
    assert len(handler.handled_messages) == 1
    assert handler.handled_messages[0] == test_message
    assert handler.error_count == 0

@pytest.mark.asyncio
async def test_handler_failure(test_message):
    """测试处理器失败"""
    handler = TestHandler(should_fail=True)
    
    with pytest.raises(RetryableError):
        await handler.handle(test_message)
    
    assert len(handler.handled_messages) == 0
    assert handler.error_count == 1

@pytest.mark.asyncio
async def test_handler_delay(test_message):
    """测试处理器延迟"""
    handler = TestHandler(delay=0.1)
    
    start_time = datetime.utcnow()
    await handler.handle(test_message)
    end_time = datetime.utcnow()
    
    duration = (end_time - start_time).total_seconds()
    assert duration >= 0.1
    assert len(handler.handled_messages) == 1

def test_retry_strategy_init():
    """测试重试策略初始化"""
    strategy = RetryStrategy(
        max_retries=3,
        base_delay=0.1,
        max_delay=1.0,
        multiplier=2.0
    )
    
    assert strategy.max_retries == 3
    assert strategy.base_delay == 0.1
    assert strategy.max_delay == 1.0
    assert strategy.multiplier == 2.0

def test_retry_strategy_get_delay():
    """测试重试策略延迟计算"""
    strategy = RetryStrategy(
        max_retries=3,
        base_delay=0.1,
        max_delay=1.0,
        multiplier=2.0
    )
    
    # 测试首次重试
    assert strategy.get_delay(1) == 0.1
    
    # 测试指数退避
    assert strategy.get_delay(2) == 0.2
    assert strategy.get_delay(3) == 0.4
    
    # 测试最大延迟限制
    assert strategy.get_delay(4) == 0.8
    assert strategy.get_delay(5) == 1.0  # 不超过max_delay

@pytest.mark.asyncio
async def test_retry_strategy_execute(test_message, retry_strategy):
    """测试重试策略执行"""
    handler = TestHandler(should_fail=True)
    
    with pytest.raises(MaxRetriesExceededError):
        await retry_strategy.execute(
            lambda: handler.handle(test_message)
        )
    
    assert handler.error_count == retry_strategy.max_retries + 1

@pytest.mark.asyncio
async def test_retry_strategy_timeout(test_message, retry_strategy):
    """测试重试策略超时"""
    handler = TestHandler(delay=0.2)  # 处理器会延迟0.2秒
    
    with pytest.raises(asyncio.TimeoutError):
        await retry_strategy.execute(
            lambda: handler.handle(test_message),
            timeout=0.1  # 设置0.1秒超时
        )
    
    assert len(handler.handled_messages) == 0

@pytest.mark.asyncio
async def test_retry_strategy_success_after_retry(test_message, retry_strategy):
    """测试重试后成功"""
    class CountingHandler(TestHandler):
        def __init__(self, fail_count: int):
            super().__init__()
            self.fail_count = fail_count
            
        async def handle(self, message: Message) -> Optional[Message]:
            if self.error_count < self.fail_count:
                self.error_count += 1
                raise RetryableError("Temporary failure")
            self.handled_messages.append(message)
            return None
    
    handler = CountingHandler(fail_count=2)
    
    await retry_strategy.execute(
        lambda: handler.handle(test_message)
    )
    
    assert handler.error_count == 2
    assert len(handler.handled_messages) == 1 