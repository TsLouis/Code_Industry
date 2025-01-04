from .base import BaseAgent
from core.comms.message import Message, MessageType

class CoordinatorAgent(BaseAgent):
    """协调者Agent"""
    def __init__(self, provider, model, broker):
        super().__init__(provider=provider, model=model, broker=broker)
        self.name = "Coordinator"
        self.product_manager_name = "Product Manager"
        self.developer_name = "Developer"

    async def handle_message(self, message: Message) -> None:
        """处理消息"""
        if message.type == MessageType.RESPONSE:
            # 根据发送者转发消息
            if message.sender == self.developer_name:
                await self.send_message(
                    MessageType.TASK,
                    self.product_manager_name,
                    message.content
                )
            elif message.sender == self.product_manager_name:
                await self.send_message(
                    MessageType.TASK,
                    self.developer_name,
                    message.content
                ) 