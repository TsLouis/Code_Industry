import asyncio
import uuid
from datetime import datetime
from pathlib import Path

from core.comms.broker import MessageBroker
from core.comms.message import MessageType
from adapters.providers.openai import OpenAIProvider
from agents.coordinator import CoordinatorAgent
from agents.product import ProductAgent
from agents.developer import DeveloperAgent
from utils.save_utils import save_conversation

class Engine:
    """引擎类"""
    def __init__(self):
        self.conversation_id = str(uuid.uuid4())
        self.messages_history = []
        self.implementation_version = 1
        
        # 创建事件
        self.review_completed = asyncio.Event()
        self.implementation_completed = asyncio.Event()
        self.all_tasks_completed = asyncio.Event()
        
        # 初始化组件
        self.broker = MessageBroker()
        self.provider = OpenAIProvider(
            api_key="sk-WGQLphVmPxKMhgPu8L6ewi0jdV6D78ht1nBm2MJRQg7Tu6wg",
            base_url="https://api.openai-proxy.org/v1"
        )
        
        # 初始化Agents
        self.coordinator = CoordinatorAgent(provider=self.provider, model="gpt-3.5-turbo", broker=self.broker)
        self.product_manager = ProductAgent(provider=self.provider, model="gpt-3.5-turbo", broker=self.broker)
        self.developer = DeveloperAgent(provider=self.provider, model="gpt-3.5-turbo", broker=self.broker)
        
        # 创建输出目录
        self.code_dir = Path("data/outputs/code")
        self.code_dir.mkdir(parents=True, exist_ok=True)

    async def start(self, task: str = None):
        """启动引擎"""
        # 启动消息代理
        broker_task = asyncio.create_task(self.broker.start())
        await asyncio.sleep(1)
        
        print(f"\n=== 开始任务 (ID: {self.conversation_id}) ===\n")
        
        # 订阅消息
        self.broker.subscribe(self.coordinator.name, self.coordinator.handle_message)
        self.broker.subscribe(self.product_manager.name, self.product_manager.handle_message)
        self.broker.subscribe(self.developer.name, self.developer.handle_message)
        
        # 发送初始任务
        if task:
            await self.send_task(task)
        else:
            # 等待用户输入任务
            task = await self.get_user_task()
            await self.send_task(task)
        
        try:
            await self.run_task_loop()
        finally:
            # 保存对话记录
            save_conversation(self.conversation_id, self.messages_history)
            print(f"对话记录已保存到: data/conversations/{datetime.now().strftime('%Y%m%d')}_{self.conversation_id}.json\n")
            
            # 停止消息代理
            print("停止消息代理...")
            await self.broker.stop()
            broker_task.cancel()
            try:
                await broker_task
            except asyncio.CancelledError:
                pass

    async def get_user_task(self) -> str:
        """获取用户输入的任务"""
        print("\n请输入任务描述（输入空行结束）：")
        lines = []
        while True:
            try:
                line = input()
                if not line:  # 如果是空行，结束输入
                    break
                lines.append(line)
            except KeyboardInterrupt:
                break
        return "\n".join(lines)

    async def send_task(self, task: str):
        """发送任务给开发者"""
        print(f"\n发送任务给开发者: {task}\n")
        await self.coordinator.send_message(
            MessageType.TASK,
            self.developer.name,
            {"task": task}
        )

    async def run_task_loop(self):
        """运行任务循环"""
        try:
            # 等待任务完成，最多3轮迭代
            for iteration in range(3):
                if self.all_tasks_completed.is_set():
                    break
                    
                print(f"\n=== 开始第 {iteration + 1} 轮迭代 ===\n")
                
                # 等待当前轮次完成
                await asyncio.wait_for(
                    asyncio.gather(
                        self.implementation_completed.wait(),
                        self.review_completed.wait()
                    ),
                    timeout=180
                )
                
                # 重置事件状态
                self.implementation_completed.clear()
                self.review_completed.clear()
                
            if not self.all_tasks_completed.is_set():
                print("\n=== 达到最大迭代次数 ===\n")
                
        except asyncio.TimeoutError:
            print("\n等待响应超时！\n")
            self.messages_history.append({
                "timestamp": datetime.now().isoformat(),
                "type": "error",
                "content": "Response timeout"
            })

    async def handle_message(self, message):
        """处理所有消息"""
        from .tasks import TaskProcessor
        
        self.messages_history.append({
            "timestamp": datetime.now().isoformat(),
            "sender": message.sender,
            "receiver": message.receiver,
            "type": message.type.value,
            "content": message.content.get('task') or message.content.get('response')
        })
        
        if message.type == MessageType.RESPONSE:
            if message.sender == self.developer.name:
                print(f"\n=== 开发者提交实现 V{self.implementation_version} ===\n")
                
                # 保存代码文件
                implementation = message.content['response']
                version_dir = self.code_dir / f"v{self.implementation_version}"
                version_dir.mkdir(exist_ok=True)
                
                # 处理开发者的响应
                has_files, required_files = await TaskProcessor.process_developer_response(implementation, version_dir)
                print(f"代码文件已保存到: {version_dir}\n")
                
                # 检查是否所有必需文件都已实现且非空
                missing_files = TaskProcessor.get_missing_files(required_files)
                if missing_files or not has_files:
                    # 如果有文件缺失或为空，要求重新提交
                    await self.coordinator.send_message(
                        MessageType.TASK,
                        self.developer.name,
                        {"task": f"""您的实现缺少一些必要的文件或有空文件。请完整实现所有必需的文件：

以下文件尚未完整实现：
{chr(10).join('- ' + f for f in missing_files)}

请提供完整的代码实现，确保：
1. 实现所有必需的文件，包括前端JavaScript和CSS
2. 每个文件都要有实际的代码实现，不能为空或只包含注释
3. 前端JavaScript需要实现与后端API的交互
4. CSS需要提供基本的样式美化
5. 使用正确的文件标注格式（如 ```python:app.py）
6. 代码必须完整可运行"""}
                    )
                else:
                    # 将实现转发给产品经理审查
                    await self.coordinator.send_message(
                        MessageType.TASK,
                        self.product_manager.name,
                        {"task": f"""请审查开发者的实现 V{self.implementation_version}，重点关注：
1. 是否使用了要求的技术栈（Flask + SQLite）
2. 功能是否完整（创建、编辑、删除、状态管理）
3. 代码结构是否清晰
4. 前端交互是否合理
5. 样式是否美观
6. 是否存在潜在问题

实现内容：
{implementation}

请提供详细的审查意见，并明确指出需要修改的部分。
如果完全满意，请明确标注"实现通过审查"。
如果需要修改，请明确列出需要改进的点。"""}
                    )
                    self.implementation_completed.set()
                
            elif message.sender == self.product_manager.name:
                print(f"\n=== 产品经理审查意见 V{self.implementation_version} ===\n{message.content['response']}\n")
                
                # 分析反馈内容，检查是否需要继续迭代
                if "实现通过审查" in message.content['response']:
                    print("\n=== 实现已通过审查 ===\n")
                    self.all_tasks_completed.set()
                else:
                    self.implementation_version += 1
                    # 将反馈发送给开发者进行修改
                    await self.coordinator.send_message(
                        MessageType.TASK,
                        self.developer.name,
                        {"task": f"""请根据产品经理的反馈修改代码实现（当前版本 V{self.implementation_version-1}）：

审查意见：
{message.content['response']}

请提供完整的修改后代码，确保：
1. 解决所有审查意见中提到的问题
2. 保持代码结构清晰
3. 提供必要的注释说明
4. 前端JavaScript实现完整的交互功能
5. CSS提供美观的样式
6. 使用正确的文件标注格式（如 ```python:app.py）
7. 提供所有必要的文件，不要遗漏任何文件
8. 代码必须完整可运行"""}
                    )
                self.review_completed.set() 