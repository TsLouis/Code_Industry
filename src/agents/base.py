import uuid
from typing import Optional
from core.comms.message import Message, MessageType
from core.comms.broker import MessageBroker
from adapters.providers.openai import OpenAIProvider
from utils.logger import setup_logger

logger = setup_logger(__name__)

class BaseAgent:
    """基础Agent类"""
    def __init__(self, provider: OpenAIProvider, model: str, broker: MessageBroker):
        self.provider = provider
        self.model = model
        self.broker = broker
        self.logger = logger

    async def send_message(self, type: MessageType, receiver: str, content: dict, reply_to: Optional[str] = None) -> None:
        """发送消息"""
        message = Message(
            id=str(uuid.uuid4()),
            type=type,
            sender=self.__class__.__name__,
            receiver=receiver,
            content=content
        )
        await self.broker.publish(message)

    async def handle_message(self, message: Message) -> None:
        """处理接收到的消息"""
        raise NotImplementedError("子类必须实现handle_message方法") 