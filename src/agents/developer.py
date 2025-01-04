from .base import BaseAgent
from core.comms.message import Message, MessageType

class DeveloperAgent(BaseAgent):
    """开发者Agent"""
    def __init__(self, provider, model, broker):
        super().__init__(provider=provider, model=model, broker=broker)
        self.name = "Developer"
        self.coordinator_name = "Coordinator"

    async def handle_message(self, message: Message) -> None:
        """处理消息"""
        if message.type == MessageType.TASK:
            # 构建系统提示
            system_prompt = """你是一个专业的开发者。你的职责是:
1. 根据需求实现具体功能
2. 编写清晰、可维护的代码
3. 确保代码质量和性能
4. 遵循最佳实践和设计模式

在编写代码时，你应该:
1. 使用正确的文件标注格式
2. 提供完整的实现
3. 添加必要的注释
4. 确保代码可以运行
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