"""
Message serialization implementation
"""

from abc import ABC, abstractmethod
import json
import msgpack
from datetime import datetime
from typing import Any, Dict, Union

from .types import Message, MessageType, MessageStatus, MessagePriority


class SerializationError(Exception):
    """序列化错误"""
    pass


class MessageSerializer(ABC):
    """消息序列化器接口"""
    
    @abstractmethod
    def serialize(self, message: Message) -> bytes:
        """序列化消息
        
        Args:
            message: 要序列化的消息
            
        Returns:
            bytes: 序列化后的字节串
            
        Raises:
            SerializationError: 序列化失败
        """
        pass
    
    @abstractmethod
    def deserialize(self, data: bytes) -> Message:
        """反序列化消息
        
        Args:
            data: 要反序列化的字节串
            
        Returns:
            Message: 反序列化后的消息
            
        Raises:
            SerializationError: 反序列化失败
        """
        pass


class JsonSerializer(MessageSerializer):
    """JSON序列化器"""
    
    def _serialize_datetime(self, obj: Any) -> str:
        """序列化datetime对象"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def _deserialize_datetime(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """反序列化datetime对象"""
        if "__datetime__" in obj:
            return datetime.fromisoformat(obj["__datetime__"])
        return obj
    
    def serialize(self, message: Message) -> bytes:
        try:
            data = message.model_dump()
            # 转换枚举值为字符串
            data["type"] = data["type"].value
            data["status"] = data["status"].value
            data["priority"] = data["priority"].value
            
            return json.dumps(
                data,
                default=self._serialize_datetime,
                ensure_ascii=False
            ).encode("utf-8")
        except Exception as e:
            raise SerializationError(f"Failed to serialize message: {str(e)}")
    
    def deserialize(self, data: bytes) -> Message:
        try:
            dict_data = json.loads(
                data.decode("utf-8"),
                object_hook=self._deserialize_datetime
            )
            
            # 转换字符串为枚举值
            dict_data["type"] = MessageType(dict_data["type"])
            dict_data["status"] = MessageStatus(dict_data["status"])
            dict_data["priority"] = MessagePriority(dict_data["priority"])
            
            return Message(**dict_data)
        except Exception as e:
            raise SerializationError(f"Failed to deserialize message: {str(e)}")


class MessagePackSerializer(MessageSerializer):
    """MessagePack序列化器"""
    
    def _encode_datetime(self, obj: Any) -> Union[Dict[str, Any], Any]:
        """编码datetime对象"""
        if isinstance(obj, datetime):
            return {
                "__datetime__": True,
                "data": obj.isoformat()
            }
        return obj
    
    def _decode_datetime(self, obj: Dict[str, Any]) -> Union[datetime, Dict[str, Any]]:
        """解码datetime对象"""
        if isinstance(obj, dict) and obj.get("__datetime__"):
            return datetime.fromisoformat(obj["data"])
        return obj
    
    def serialize(self, message: Message) -> bytes:
        try:
            data = message.model_dump()
            # 转换枚举值为字符串
            data["type"] = data["type"].value
            data["status"] = data["status"].value
            data["priority"] = data["priority"].value
            
            return msgpack.packb(
                data,
                default=self._encode_datetime,
                use_bin_type=True
            )
        except Exception as e:
            raise SerializationError(f"Failed to serialize message: {str(e)}")
    
    def deserialize(self, data: bytes) -> Message:
        try:
            dict_data = msgpack.unpackb(
                data,
                object_hook=self._decode_datetime,
                raw=False
            )
            
            # 转换字符串为枚举值
            dict_data["type"] = MessageType(dict_data["type"])
            dict_data["status"] = MessageStatus(dict_data["status"])
            dict_data["priority"] = MessagePriority(dict_data["priority"])
            
            return Message(**dict_data)
        except Exception as e:
            raise SerializationError(f"Failed to deserialize message: {str(e)}") 