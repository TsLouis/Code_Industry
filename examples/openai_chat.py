import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.adapters.providers.openai.config import create_openai_config
from src.adapters.providers.openai.client import OpenAIAdapter

async def main():
    # 创建配置
    config = create_openai_config(
        api_key="sk-WGQLphVmPxKMhgPu8L6ewi0jdV6D78ht1nBm2MJRQg7Tu6wg",
        model_name="gpt-3.5-turbo",
        base_url="https://api.openai-proxy.org/v1"
    )
    
    # 初始化适配器
    adapter = OpenAIAdapter(config)
    
    # 准备消息
    messages = [
        {"role": "user", "content": "你好，请介绍一下你自己。"}
    ]
    
    try:
        # 发送请求
        response = await adapter.chat_completion(messages)
        print(f"AI: {response.content}")
        
        # 打印使用情况
        print("\n使用统计:")
        print(f"Prompt tokens: {response.usage['prompt_tokens']}")
        print(f"Completion tokens: {response.usage['completion_tokens']}")
        print(f"Total tokens: {response.usage['total_tokens']}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 