import asyncio
from typing import Dict, Callable, List, Awaitable, Any, Set
from core.comms.message import Message, MessageType
from utils.logger import setup_logger

logger = setup_logger(__name__)

class MessageBroker:
    """简单的消息代理"""
    def __init__(self):
        self._subscribers: Dict[str, Set[Callable[[Message], Awaitable[Any]]]] = {}
        self._message_queue = asyncio.Queue()
        self._running = False
        self.logger = setup_logger("MessageBroker", "broker")

    async def start(self):
        """启动消息处理"""
        self._running = True
        self.logger.info("消息代理启动")
        while self._running:
            message = await self._message_queue.get()
            if isinstance(message, Message):
                self.logger.debug(f"收到消息: {message.type} from {message.sender} to {message.receiver}")
                if message.receiver in self._subscribers:
                    for handler in self._subscribers[message.receiver]:
                        try:
                            await handler(message)
                        except Exception as e:
                            self.logger.error(f"处理消息时出错: {e}", exc_info=True)
                self._message_queue.task_done()

    async def stop(self):
        """停止消息处理"""
        self.logger.info("正在停止消息代理...")
        self._running = False
        await self._message_queue.put(Message(
            id="system",
            type=MessageType.INFO,
            sender="system",
            receiver="system",
            content={"action": "stop"}
        ))

    async def publish(self, message: Message):
        """发布消息"""
        if self._running:
            self.logger.debug(f"发布消息: {message.type} from {message.sender} to {message.receiver}")
            await self._message_queue.put(message)

    def subscribe(self, agent_id: str, handler: Callable[[Message], Awaitable[Any]]):
        """订阅消息"""
        self.logger.info(f"Agent {agent_id} 订阅消息")
        if agent_id not in self._subscribers:
            self._subscribers[agent_id] = set()
        self._subscribers[agent_id].add(handler)

    def unsubscribe(self, agent_id: str, handler: Callable[[Message], Awaitable[Any]]):
        """取消订阅"""
        self.logger.info(f"Agent {agent_id} 取消订阅")
        if agent_id in self._subscribers:
            self._subscribers[agent_id].discard(handler) 