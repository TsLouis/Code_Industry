from .base import BaseAgent
from core.comms.message import Message, MessageType

class ProductAgent(BaseAgent):
    """产品经理Agent"""
    def __init__(self, provider, model, broker):
        super().__init__(provider=provider, model=model, broker=broker)
        self.name = "Product Manager"
        self.coordinator_name = "Coordinator"

    async def handle_message(self, message: Message) -> None:
        """处理消息"""
        if message.type == MessageType.TASK:
            # 构建系统提示
            system_prompt = """你是一个产品经理。你的职责是:
1. 审查开发者提交的代码实现
2. 确保功能完整性和用户体验
3. 提供具体的改进建议
4. 明确标注是否通过审查

在审查时，你应该关注:
1. 功能是否符合需求
2. 代码结构是否清晰
3. 用户界面是否合理
4. 是否存在潜在问题
"""
            # 构建用户消息
            user_message = message.content.get('task')
            
            # 调用API获取响应
            response = ""
            async for chunk in self.provider.chat([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ], model=self.model):
                response += chunk
            
            # 发送响应
            await self.send_message(
                MessageType.RESPONSE,
                self.coordinator_name,
                {"response": response}
            ) 