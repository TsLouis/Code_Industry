"""Test cases for message serialization"""
import pytest
from datetime import datetime
import json
import msgpack

from src.core.comms.types import Message, MessageType, MessagePriority, MessageStatus
from src.core.comms.serialization import (
    JsonSerializer,
    MessagePackSerializer,
    SerializationError
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

@pytest.fixture
def json_serializer():
    """创建JSON序列化器"""
    return JsonSerializer()

@pytest.fixture
def msgpack_serializer():
    """创建MessagePack序列化器"""
    return MessagePackSerializer()

def test_json_serializer_serialize(json_serializer, test_message):
    """测试JSON序列化"""
    # 序列化消息
    data = json_serializer.serialize(test_message)
    assert isinstance(data, bytes)
    
    # 验证序列化结果
    json_data = json.loads(data.decode("utf-8"))
    assert json_data["id"] == test_message.id
    assert json_data["type"] == test_message.type.value
    assert json_data["priority"] == test_message.priority.value
    assert json_data["sender"] == test_message.sender
    assert json_data["receiver"] == test_message.receiver
    assert json_data["content"] == test_message.content
    assert json_data["trace_id"] == test_message.trace_id
    assert json_data["timeout"] == test_message.timeout
    assert json_data["status"] == test_message.status.value

def test_json_serializer_deserialize(json_serializer, test_message):
    """测试JSON反序列化"""
    # 序列化后再反序列化
    data = json_serializer.serialize(test_message)
    message = json_serializer.deserialize(data)
    
    # 验证反序列化结果
    assert message.id == test_message.id
    assert message.type == test_message.type
    assert message.priority == test_message.priority
    assert message.sender == test_message.sender
    assert message.receiver == test_message.receiver
    assert message.content == test_message.content
    assert message.trace_id == test_message.trace_id
    assert message.timeout == test_message.timeout
    assert message.status == test_message.status

def test_json_serializer_error_handling(json_serializer):
    """测试JSON序列化错误处理"""
    # 测试序列化无效对象
    with pytest.raises(SerializationError):
        json_serializer.serialize(object())
    
    # 测试反序列化无效数据
    with pytest.raises(SerializationError):
        json_serializer.deserialize(b"invalid json")

def test_msgpack_serializer_serialize(msgpack_serializer, test_message):
    """测试MessagePack序列化"""
    # 序列化消息
    data = msgpack_serializer.serialize(test_message)
    assert isinstance(data, bytes)
    
    # 验证序列化结果
    msgpack_data = msgpack.unpackb(data, raw=False)
    assert msgpack_data["id"] == test_message.id
    assert msgpack_data["type"] == test_message.type.value
    assert msgpack_data["priority"] == test_message.priority.value
    assert msgpack_data["sender"] == test_message.sender
    assert msgpack_data["receiver"] == test_message.receiver
    assert msgpack_data["content"] == test_message.content
    assert msgpack_data["trace_id"] == test_message.trace_id
    assert msgpack_data["timeout"] == test_message.timeout
    assert msgpack_data["status"] == test_message.status.value

def test_msgpack_serializer_deserialize(msgpack_serializer, test_message):
    """测试MessagePack反序列化"""
    # 序列化后再反序列化
    data = msgpack_serializer.serialize(test_message)
    message = msgpack_serializer.deserialize(data)
    
    # 验证反序列化结果
    assert message.id == test_message.id
    assert message.type == test_message.type
    assert message.priority == test_message.priority
    assert message.sender == test_message.sender
    assert message.receiver == test_message.receiver
    assert message.content == test_message.content
    assert message.trace_id == test_message.trace_id
    assert message.timeout == test_message.timeout
    assert message.status == test_message.status

def test_msgpack_serializer_error_handling(msgpack_serializer):
    """测试MessagePack序列化错误处理"""
    # 测试序列化无效对象
    with pytest.raises(SerializationError):
        msgpack_serializer.serialize(object())
    
    # 测试反序列化无效数据
    with pytest.raises(SerializationError):
        msgpack_serializer.deserialize(b"invalid msgpack")

def test_json_serializer_empty_content(json_serializer):
    """测试JSON序列化空内容"""
    message = Message(
        id="test_id",
        type=MessageType.TASK,
        priority=MessagePriority.MEDIUM,
        sender="test_sender",
        receiver="test_receiver",
        content={},  # 空内容
        timestamp=datetime.utcnow(),
        trace_id="test_trace",
        timeout=60,
        status=MessageStatus.PENDING
    )
    
    data = json_serializer.serialize(message)
    result = json_serializer.deserialize(data)
    assert result.content == {}

def test_json_serializer_special_chars(json_serializer):
    """测试JSON序列化特殊字符"""
    message = Message(
        id="test_id",
        type=MessageType.TASK,
        priority=MessagePriority.MEDIUM,
        sender="test_sender",
        receiver="test_receiver",
        content={"special": "!@#$%^&*()_+-=[]{}|;:'\",.<>?/\\"},
        timestamp=datetime.utcnow(),
        trace_id="test_trace",
        timeout=60,
        status=MessageStatus.PENDING
    )
    
    data = json_serializer.serialize(message)
    result = json_serializer.deserialize(data)
    assert result.content["special"] == "!@#$%^&*()_+-=[]{}|;:'\",.<>?/\\"

def test_json_serializer_large_message(json_serializer):
    """测试JSON序列化大消息"""
    large_content = {"data": "x" * 1000000}  # 1MB的数据
    message = Message(
        id="test_id",
        type=MessageType.TASK,
        priority=MessagePriority.MEDIUM,
        sender="test_sender",
        receiver="test_receiver",
        content=large_content,
        timestamp=datetime.utcnow(),
        trace_id="test_trace",
        timeout=60,
        status=MessageStatus.PENDING
    )
    
    data = json_serializer.serialize(message)
    result = json_serializer.deserialize(data)
    assert len(result.content["data"]) == 1000000

def test_msgpack_serializer_empty_content(msgpack_serializer):
    """测试MessagePack序列化空内容"""
    message = Message(
        id="test_id",
        type=MessageType.TASK,
        priority=MessagePriority.MEDIUM,
        sender="test_sender",
        receiver="test_receiver",
        content={},  # 空内容
        timestamp=datetime.utcnow(),
        trace_id="test_trace",
        timeout=60,
        status=MessageStatus.PENDING
    )
    
    data = msgpack_serializer.serialize(message)
    result = msgpack_serializer.deserialize(data)
    assert result.content == {}

def test_msgpack_serializer_binary_content(msgpack_serializer):
    """测试MessagePack序列化二进制内容"""
    binary_data = bytes([i % 256 for i in range(1000)])
    message = Message(
        id="test_id",
        type=MessageType.TASK,
        priority=MessagePriority.MEDIUM,
        sender="test_sender",
        receiver="test_receiver",
        content={"binary": binary_data},
        timestamp=datetime.utcnow(),
        trace_id="test_trace",
        timeout=60,
        status=MessageStatus.PENDING
    )
    
    data = msgpack_serializer.serialize(message)
    result = msgpack_serializer.deserialize(data)
    assert result.content["binary"] == binary_data

def test_msgpack_serializer_large_message(msgpack_serializer):
    """测试MessagePack序列化大消息"""
    large_content = {"data": bytes([i % 256 for i in range(1000000)])}  # 1MB的二进制数据
    message = Message(
        id="test_id",
        type=MessageType.TASK,
        priority=MessagePriority.MEDIUM,
        sender="test_sender",
        receiver="test_receiver",
        content=large_content,
        timestamp=datetime.utcnow(),
        trace_id="test_trace",
        timeout=60,
        status=MessageStatus.PENDING
    )
    
    data = msgpack_serializer.serialize(message)
    result = msgpack_serializer.deserialize(data)
    assert len(result.content["data"]) == 1000000 