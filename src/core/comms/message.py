from enum import Enum
from typing import Dict, Any
from dataclasses import dataclass

class MessageType(Enum):
    """消息类型"""
    TASK = "task"         # 任务
    RESPONSE = "response" # 响应
    INFO = "info"         # 信息
    ERROR = "error"       # 错误

@dataclass
class Message:
    """消息类"""
    id: str                  # 消息ID
    type: MessageType        # 消息类型
    sender: str             # 发送者
    receiver: str           # 接收者
    content: Dict[str, Any] # 消息内容 