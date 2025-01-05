"""Test cases for message broker"""
import pytest
import asyncio
from datetime import datetime
from typing import List, Optional

from src.core.comms.types import Message, MessageType, MessagePriority, MessageStatus
from src.core.comms.broker import MessageBroker, Subscription
from src.core.comms.filters import TypeFilter

class TestSubscriber:
    """测试用的订阅者"""
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
def broker():
    """创建消息代理"""
    return MessageBroker()

@pytest.mark.asyncio
async def test_broker_subscribe(broker):
    """测试订阅"""
    subscriber = TestSubscriber()
    filter = TypeFilter([MessageType.TASK])
    
    # 添加订阅
    subscription = broker.subscribe(subscriber.handle, filter)
    assert isinstance(subscription, Subscription)
    assert len(broker.subscriptions) == 1

@pytest.mark.asyncio
async def test_broker_unsubscribe(broker):
    """测试取消订阅"""
    subscriber = TestSubscriber()
    filter = TypeFilter([MessageType.TASK])
    
    # 添加订阅
    subscription = broker.subscribe(subscriber.handle, filter)
    assert len(broker.subscriptions) == 1
    
    # 取消订阅
    broker.unsubscribe(subscription)
    assert len(broker.subscriptions) == 0

@pytest.mark.asyncio
async def test_broker_publish(broker, test_message):
    """测试发布消息"""
    subscriber = TestSubscriber()
    filter = TypeFilter([MessageType.TASK])
    
    # 添加订阅
    broker.subscribe(subscriber.handle, filter)
    
    # 发布消息
    await broker.publish(test_message)
    
    # 验证消息是否被处理
    assert len(subscriber.messages) == 1
    assert subscriber.messages[0] == test_message

@pytest.mark.asyncio
async def test_broker_multiple_subscribers(broker, test_message):
    """测试多个订阅者"""
    subscriber1 = TestSubscriber()
    subscriber2 = TestSubscriber()
    filter = TypeFilter([MessageType.TASK])
    
    # 添加订阅
    broker.subscribe(subscriber1.handle, filter)
    broker.subscribe(subscriber2.handle, filter)
    
    # 发布消息
    await broker.publish(test_message)
    
    # 验证所有订阅者都收到消息
    assert len(subscriber1.messages) == 1
    assert len(subscriber2.messages) == 1

@pytest.mark.asyncio
async def test_broker_filter_matching(broker, test_message):
    """测试过滤器匹配"""
    subscriber = TestSubscriber()
    
    # 添加匹配的过滤器
    filter1 = TypeFilter([MessageType.TASK])
    broker.subscribe(subscriber.handle, filter1)
    
    # 添加不匹配的过滤器
    filter2 = TypeFilter([MessageType.ERROR])
    broker.subscribe(subscriber.handle, filter2)
    
    # 发布消息
    await broker.publish(test_message)
    
    # 验证只有匹配的订阅收到消息
    assert len(subscriber.messages) == 1

@pytest.mark.asyncio
async def test_broker_message_ordering(broker):
    """测试消息顺序"""
    subscriber = TestSubscriber()
    filter = TypeFilter([MessageType.TASK])
    broker.subscribe(subscriber.handle, filter)
    
    # 创建多个消息
    messages = [
        Message(
            id=f"id_{i}",
            type=MessageType.TASK,
            priority=MessagePriority.MEDIUM,
            sender="test_sender",
            receiver="test_receiver",
            content={"value": i},
            timestamp=datetime.utcnow(),
            trace_id="test_trace",
            timeout=60,
            status=MessageStatus.PENDING
        )
        for i in range(5)
    ]
    
    # 发布所有消息
    for msg in messages:
        await broker.publish(msg)
    
    # 验证消息顺序
    assert len(subscriber.messages) == 5
    for i, msg in enumerate(subscriber.messages):
        assert msg.content["value"] == i

@pytest.mark.asyncio
async def test_broker_error_handling(broker, test_message):
    """测试错误处理"""
    async def error_handler(message: Message):
        raise Exception("Test error")
    
    # 添加会抛出异常的处理器
    broker.subscribe(error_handler, TypeFilter([MessageType.TASK]))
    
    # 发布消息不应该抛出异常
    await broker.publish(test_message)

@pytest.mark.asyncio
async def test_broker_subscription_priority(broker, test_message):
    """测试订阅优先级"""
    messages = []
    
    async def handler1(message: Message):
        messages.append(1)
        
    async def handler2(message: Message):
        messages.append(2)
    
    # 添加不同优先级的订阅
    broker.subscribe(handler2, TypeFilter([MessageType.TASK]), priority=2)
    broker.subscribe(handler1, TypeFilter([MessageType.TASK]), priority=1)
    
    # 发布消息
    await broker.publish(test_message)
    
    # 验证处理顺序
    assert messages == [2, 1]  # 高优先级先处理 

@pytest.mark.asyncio
async def test_broker_concurrent_publish(broker, test_message):
    """测试并发发布消息"""
    subscriber = TestSubscriber()
    filter = TypeFilter([MessageType.TASK])
    broker.subscribe(subscriber.handle, filter)
    
    # 创建多个消息
    messages = [
        Message(
            id=f"id_{i}",
            type=MessageType.TASK,
            priority=MessagePriority.MEDIUM,
            sender="test_sender",
            receiver="test_receiver",
            content={"value": i},
            timestamp=datetime.utcnow(),
            trace_id="test_trace",
            timeout=60,
            status=MessageStatus.PENDING
        )
        for i in range(100)
    ]
    
    # 并发发布所有消息
    await asyncio.gather(*[broker.publish(msg) for msg in messages])
    
    # 验证所有消息都被处理
    assert len(subscriber.messages) == 100
    received_values = {msg.content["value"] for msg in subscriber.messages}
    expected_values = set(range(100))
    assert received_values == expected_values

@pytest.mark.asyncio
async def test_broker_concurrent_subscribe_unsubscribe(broker, test_message):
    """测试并发订阅和取消订阅"""
    subscribers = [TestSubscriber() for _ in range(10)]
    filter = TypeFilter([MessageType.TASK])
    
    # 并发订阅
    subscriptions = await asyncio.gather(*[
        asyncio.create_task(
            asyncio.to_thread(broker.subscribe, sub.handle, filter)
        )
        for sub in subscribers
    ])
    
    # 验证所有订阅都成功
    assert len(broker.subscriptions) == 10
    
    # 发布一条消息
    await broker.publish(test_message)
    
    # 验证所有订阅者都收到消息
    for sub in subscribers:
        assert len(sub.messages) == 1
    
    # 并发取消订阅
    await asyncio.gather(*[
        asyncio.create_task(
            asyncio.to_thread(broker.unsubscribe, sub)
        )
        for sub in subscriptions
    ])
    
    # 验证所有订阅都被取消
    assert len(broker.subscriptions) == 0

@pytest.mark.asyncio
async def test_broker_concurrent_mixed_operations(broker):
    """测试混合并发操作"""
    async def publish_messages(count: int):
        messages = [
            Message(
                id=f"id_{i}",
                type=MessageType.TASK,
                priority=MessagePriority.MEDIUM,
                sender="test_sender",
                receiver="test_receiver",
                content={"value": i},
                timestamp=datetime.utcnow(),
                trace_id="test_trace",
                timeout=60,
                status=MessageStatus.PENDING
            )
            for i in range(count)
        ]
        await asyncio.gather(*[broker.publish(msg) for msg in messages])
    
    async def subscribe_unsubscribe(iterations: int):
        for _ in range(iterations):
            subscriber = TestSubscriber()
            filter = TypeFilter([MessageType.TASK])
            subscription = broker.subscribe(subscriber.handle, filter)
            await asyncio.sleep(0.01)  # 模拟一些处理时间
            broker.unsubscribe(subscription)
    
    # 并发执行多个操作
    await asyncio.gather(
        publish_messages(50),
        subscribe_unsubscribe(20),
        publish_messages(50)
    )
    
    # 验证代理状态
    assert len(broker.subscriptions) == 0  # 所有订阅都应该被取消

@pytest.mark.asyncio
async def test_broker_stress_test(broker):
    """压力测试消息代理"""
    message_count = 1000
    subscriber_count = 10
    
    # 创建多个订阅者
    subscribers = [TestSubscriber() for _ in range(subscriber_count)]
    filter = TypeFilter([MessageType.TASK])
    for sub in subscribers:
        broker.subscribe(sub.handle, filter)
    
    # 创建大量消息
    messages = [
        Message(
            id=f"id_{i}",
            type=MessageType.TASK,
            priority=MessagePriority.MEDIUM,
            sender="test_sender",
            receiver="test_receiver",
            content={"value": i},
            timestamp=datetime.utcnow(),
            trace_id="test_trace",
            timeout=60,
            status=MessageStatus.PENDING
        )
        for i in range(message_count)
    ]
    
    # 并发发布所有消息
    start_time = datetime.utcnow()
    await asyncio.gather(*[broker.publish(msg) for msg in messages])
    end_time = datetime.utcnow()
    
    # 计算处理时间和速率
    duration = (end_time - start_time).total_seconds()
    messages_per_second = message_count / duration
    
    # 验证所有消息都被所有订阅者处理
    for sub in subscribers:
        assert len(sub.messages) == message_count
        received_values = {msg.content["value"] for msg in sub.messages}
        expected_values = set(range(message_count))
        assert received_values == expected_values 