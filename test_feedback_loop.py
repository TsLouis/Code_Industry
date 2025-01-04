import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from src.core.comms.broker import MessageBroker
from src.core.comms.message import MessageType
from adapters.providers.openai import OpenAIProvider
from src.agents.coordinator import CoordinatorAgent
from src.agents.product import ProductAgent
from src.agents.developer import DeveloperAgent
from src.utils.save_utils import save_conversation

async def main():
    conversation_id = str(uuid.uuid4())
    messages_history = []
    
    # 创建代码输出目录
    code_dir = Path("data/outputs/code")
    code_dir.mkdir(parents=True, exist_ok=True)
    
    # 初始化消息代理和Provider
    broker = MessageBroker()
    provider = OpenAIProvider(
        api_key="sk-WGQLphVmPxKMhgPu8L6ewi0jdV6D78ht1nBm2MJRQg7Tu6wg",
        base_url="https://api.openai-proxy.org/v1"
    )
    
    # 初始化Agents
    coordinator = CoordinatorAgent(provider=provider, model="gpt-3.5-turbo", broker=broker)
    product_manager = ProductAgent(provider=provider, model="gpt-3.5-turbo", broker=broker)
    developer = DeveloperAgent(provider=provider, model="gpt-3.5-turbo", broker=broker)
    
    # 启动消息代理
    broker_task = asyncio.create_task(broker.start())
    await asyncio.sleep(1)
    
    print(f"\n=== 开始反馈循环测试 (ID: {conversation_id}) ===\n")
    
    # 任务状态跟踪
    implementation_version = 1
    review_completed = asyncio.Event()
    implementation_completed = asyncio.Event()
    all_tasks_completed = asyncio.Event()
    
    async def process_developer_response(implementation, version_dir):
        """处理开发者的响应，保存文件并检查完整性"""
        current_file = None
        current_content = []
        has_files = False
        required_files = {
            'app.py': False,
            'models.py': False,
            'static/js/main.js': False,
            'static/css/style.css': False,
            'templates/index.html': False,
            'requirements.txt': False
        }
        
        # 解析并保存代码文件
        for line in implementation.split('\n'):
            if line.startswith('```'):
                if current_file and current_content:
                    # 保存当前文件
                    current_file.parent.mkdir(parents=True, exist_ok=True)
                    file_content = '\n'.join(current_content)
                    current_file.write_text(file_content, encoding='utf-8')
                    has_files = True
                    
                    # 检查文件是否为空或只包含注释
                    is_empty = all(l.strip().startswith('//') or l.strip().startswith('/*') or not l.strip() 
                                 for l in current_content)
                    if not is_empty:
                        file_path = str(current_file.relative_to(version_dir))
                        if file_path in required_files:
                            required_files[file_path] = True
                
                if ':' in line:
                    # 开始新文件
                    file_path = line.split(':', 1)[1].strip()
                    current_file = version_dir / file_path
                    current_content = []
                else:
                    current_file = None
                    current_content = []
            elif current_file and not line.startswith('```'):
                current_content.append(line)
        
        # 保存最后一个文件
        if current_file and current_content:
            current_file.parent.mkdir(parents=True, exist_ok=True)
            file_content = '\n'.join(current_content)
            current_file.write_text(file_content, encoding='utf-8')
            has_files = True
            
            is_empty = all(l.strip().startswith('//') or l.strip().startswith('/*') or not l.strip() 
                          for l in current_content)
            if not is_empty:
                file_path = str(current_file.relative_to(version_dir))
                if file_path in required_files:
                    required_files[file_path] = True
        
        return has_files, required_files
    
    # 处理所有消息
    async def handle_message(message):
        nonlocal implementation_version
        
        messages_history.append({
            "timestamp": datetime.now().isoformat(),
            "sender": message.sender,
            "receiver": message.receiver,
            "type": message.type.value,
            "content": message.content.get('task') or message.content.get('response')
        })
        
        if message.type == MessageType.RESPONSE:
            if message.sender == "Developer":
                print(f"\n=== 开发者提交实现 V{implementation_version} ===\n")
                
                # 保存代码文件
                implementation = message.content['response']
                version_dir = code_dir / f"v{implementation_version}"
                version_dir.mkdir(exist_ok=True)
                
                # 处理开发者的响应
                has_files, required_files = await process_developer_response(implementation, version_dir)
                print(f"代码文件已保存到: {version_dir}\n")
                
                # 检查是否所有必需文件都已实现且非空
                missing_files = [f for f, implemented in required_files.items() if not implemented]
                if missing_files or not has_files:
                    # 如果有文件缺失或为空，要求重新提交
                    await coordinator.send_message(
                        MessageType.TASK,
                        "Developer",
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
                    await coordinator.send_message(
                        MessageType.TASK,
                        "Product Manager",
                        {"task": f"""请审查开发者的实现 V{implementation_version}，重点关注：
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
                    implementation_completed.set()
                
            elif message.sender == "Product Manager":
                print(f"\n=== 产品经理审查意见 V{implementation_version} ===\n{message.content['response']}\n")
                
                # 分析反馈内容，检查是否需要继续迭代
                if "实现通过审查" in message.content['response']:
                    print("\n=== 实现已通过审查 ===\n")
                    all_tasks_completed.set()
                else:
                    implementation_version += 1
                    # 将反馈发送给开发者进行修改
                    await coordinator.send_message(
                        MessageType.TASK,
                        "Developer",
                        {"task": f"""请根据产品经理的反馈修改代码实现（当前版本 V{implementation_version-1}）：

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
                review_completed.set()

    # 订阅所有Agent的消息
    for agent_name in ["Coordinator", "Product Manager", "Developer"]:
        broker.subscribe(agent_name, handle_message)
    
    # 发送初始任务给开发者
    initial_task = """请实现一个基于Flask和SQLite的待办事项应用，要求：

技术要求：
1. 后端使用Flask框架
2. 数据库使用SQLite
3. 前端使用HTML + JavaScript
4. 所有代码必须分文件保存，不要都写在一个文件里

功能要求：
1. 实现待办事项的创建、编辑、删除功能
2. 支持待办事项状态管理（未完成、已完成）
3. 实现美观的用户界面
4. 良好的交互体验

请提供以下文件的完整实现：
1. app.py: Flask应用主文件
2. models.py: 数据库模型定义
3. static/js/main.js: 前端JavaScript代码（实现与后端API的交互）
4. static/css/style.css: 样式文件（提供美观的界面）
5. templates/index.html: 主页面模板
6. requirements.txt: 项目依赖

每个文件都必须使用 ```python:文件路径 或 ```html:文件路径 等格式标注。
代码必须完整可运行，包含所有必要的导入语句和配置。"""

    print(f"协调者发送任务给开发者: {initial_task}\n")
    
    await coordinator.send_message(
        MessageType.TASK,
        "Developer",
        {"task": initial_task}
    )
    
    print("等待反馈循环完成...\n")
    
    try:
        # 等待任务完成，最多3轮迭代
        for iteration in range(3):
            if all_tasks_completed.is_set():
                break
                
            print(f"\n=== 开始第 {iteration + 1} 轮迭代 ===\n")
            
            # 等待当前轮次完成
            await asyncio.wait_for(
                asyncio.gather(
                    implementation_completed.wait(),
                    review_completed.wait()
                ),
                timeout=180  # 增加超时时间到3分钟
            )
            
            # 重置事件状态，准备下一轮迭代
            implementation_completed.clear()
            review_completed.clear()
            
        if not all_tasks_completed.is_set():
            print("\n=== 达到最大迭代次数 ===\n")
            
    except asyncio.TimeoutError:
        print("\n等待响应超时！\n")
        messages_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "error",
            "content": "Response timeout"
        })
    finally:
        save_conversation(conversation_id, messages_history)
        print(f"对话记录已保存到: data/conversations/{datetime.now().strftime('%Y%m%d')}_{conversation_id}.json\n")
    
    print("停止消息代理...")
    await broker.stop()
    broker_task.cancel()
    
    try:
        await broker_task
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    asyncio.run(main()) 