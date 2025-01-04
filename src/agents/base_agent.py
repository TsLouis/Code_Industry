from typing import List, Optional, Dict, AsyncIterator
from uuid import uuid4
from pydantic import BaseModel
from adapters.base.interface import LLMProvider
from adapters.base.types import Message as LLMMessage
from adapters.base.types import ChatRequest
from src.core.comms.message import Message as CommMessage
from src.core.comms.message import MessageType
from src.core.comms.broker import MessageBroker
from src.utils.logger import setup_logger

class AgentContext(BaseModel):
    """Agent上下文"""
    conversation_id: str
    messages: List[LLMMessage] = []
    metadata: Dict = {}

class BaseAgent:
    """Agent基类"""
    def __init__(
        self,
        name: str,
        provider: LLMProvider,
        model: str,
        system_prompt: str,
        broker: MessageBroker
    ):
        self.name = name
        self.provider = provider
        self.model = model
        self.system_prompt = system_prompt
        self.context = AgentContext(conversation_id="")
        self.broker = broker
        self.logger = setup_logger(f"Agent_{name}", f"agent_{name.lower()}")
        
        # 订阅消息
        self.broker.subscribe(self.name, self._handle_message)
        self.logger.info(f"Agent {name} 初始化完成")

    async def _handle_message(self, message: CommMessage):
        """处理接收到的消息"""
        self.logger.info(f"收到消息: {message.type} from {message.sender}")
        if message.type == MessageType.TASK:
            self.logger.info(f"开始处理任务: {message.content['task'][:100]}...")
            try:
                response = await self.think(message.content["task"])
                self.logger.info("任务处理完成，发送响应")
                # 发送响应给原始发送者
                await self.send_message(
                    MessageType.RESPONSE,
                    message.sender,
                    {"response": response},
                    reply_to=message.id
                )
            except Exception as e:
                self.logger.error(f"处理任务时出错: {e}", exc_info=True)
                # 发送错误响应
                await self.send_message(
                    MessageType.RESPONSE,
                    message.sender,
                    {"error": str(e)},
                    reply_to=message.id
                )

    async def send_message(
        self,
        msg_type: MessageType,
        receiver: str,
        content: Dict,
        reply_to: Optional[str] = None
    ):
        """发送消息"""
        self.logger.debug(f"发送消息到 {receiver}: {msg_type}")
        message = CommMessage(
            id=str(uuid4()),
            type=msg_type,
            sender=self.name,
            receiver=receiver,
            content=content,
            reply_to=reply_to
        )
        await self.broker.publish(message)

    async def think(self, message: str) -> str:
        """思考并回复"""
        # 添加系统提示和历史消息
        messages = [
            LLMMessage(role="system", content=self.system_prompt),
            *self.context.messages,
            LLMMessage(role="user", content=message)
        ]

        # 调用LLM
        response = await self.provider.chat_completion(
            ChatRequest(
                model=self.model,
                messages=messages
            )
        )

        # 保存对话历史
        self.context.messages.extend([
            LLMMessage(role="user", content=message),
            LLMMessage(role="assistant", content=response.choices[0]["message"]["content"])
        ])

        return response.choices[0]["message"]["content"]

    async def stream_think(self, message: str) -> AsyncIterator[str]:
        """流式思考"""
        messages = [
            LLMMessage(role="system", content=self.system_prompt),
            *self.context.messages,
            LLMMessage(role="user", content=message)
        ]

        async for chunk in self.provider.stream_chat_completion(
            ChatRequest(
                model=self.model,
                messages=messages
            )
        ):
            yield chunk.choices[0]["delta"]["content"] 