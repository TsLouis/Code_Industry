import asyncio
import argparse
from core.engine import Engine

async def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='代码生成系统')
    parser.add_argument('--task', '-t', help='要执行的任务描述')
    args = parser.parse_args()

    # 创建并启动引擎
    engine = Engine()
    await engine.start(args.task)

if __name__ == "__main__":
    asyncio.run(main()) 