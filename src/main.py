"""
多智能体协作系统主程序
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from src.core.engine import Engine, TaskConfig
from src.core.monitoring import logger

async def process_task(engine: Engine, task_input: str) -> Dict[str, Any]:
    """处理单个任务"""
    try:
        # 创建任务配置
        config = TaskConfig(
            max_steps=10,
            timeout=300.0,
            allow_parallel=True
        )
        
        # 执行任务
        result = await engine.process_input(task_input, config)
        return result
        
    except Exception as e:
        logging.error(f"任务处理失败: {str(e)}")
        raise

async def main():
    """主程序入口"""
    try:
        # 初始化日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 初始化引擎
        logging.info("正在初始化引擎...")
        engine = Engine()
        engine = await engine.initialize()
        logging.info("引擎初始化完成")
        
        while True:
            try:
                # 获取用户输入
                user_input = input("\n请输入任务描述 (输入 'exit' 退出): ")
                if user_input.lower() == 'exit':
                    break
                    
                # 处理任务
                logging.info(f"开始处理任务: {user_input}")
                start_time = datetime.now()
                
                result = await process_task(engine, user_input)
                
                # 输出结果
                execution_time = (datetime.now() - start_time).total_seconds()
                logging.info(f"任务处理完成，耗时: {execution_time:.2f}秒")
                logging.info(f"任务状态: {result['status']}")
                logging.info(f"成功步骤数: {result['success_count']}")
                logging.info(f"失败步骤数: {result['failure_count']}")
                
                if result['status'] == 'completed':
                    logging.info("\n=== 任务执行结果 ===")
                    
                    # 显示协调者输出
                    logging.info("\n--- 协调者输出 ---")
                    coordinator_results = {k: v for k, v in result['results'].items() if k.startswith('coordinator_')}
                    for key, value in coordinator_results.items():
                        logging.info(f"- {key}:")
                        logging.info(f"  {value}")
                    
                    # 显示产品经理输出
                    logging.info("\n--- 产品经理输出 ---")
                    pm_results = {k: v for k, v in result['results'].items() if k.startswith('product_manager_')}
                    for key, value in pm_results.items():
                        logging.info(f"- {key}:")
                        logging.info(f"  {value}")
                    
                    # 显示开发者输出
                    logging.info("\n--- 开发者输出 ---")
                    dev_results = {k: v for k, v in result['results'].items() if k.startswith('developer_')}
                    for key, value in dev_results.items():
                        logging.info(f"- {key}:")
                        logging.info(f"  {value}")
                    
                    # 显示生成的文件位置
                    if 'saved_files' in result['results'].get('developer_process', {}):
                        logging.info(f"\n生成的文件保存在: {result['results']['developer_process']['saved_files']}")
                    
                    # 显示任务执行历史
                    logging.info("\n--- 执行历史 ---")
                    for entry in result['history']:
                        logging.info(f"- {entry['stage']} ({entry['timestamp']})")
                else:
                    logging.warning("\n任务执行部分失败，错误信息:")
                    for key, error in result['errors'].items():
                        logging.error(f"- {key}: {error}")
                        
                # 显示监控信息位置
                logging.info(f"\n详细的Agent输出和监控信息保存在: output/agent_outputs/{result['task_id']}/")
                        
            except KeyboardInterrupt:
                logging.info("\n收到中断信号，正在退出...")
                break
            except Exception as e:
                logging.error(f"发生错误: {str(e)}")
                continue
                
    except Exception as e:
        logging.error(f"程序运行错误: {str(e)}")
        raise
    finally:
        logging.info("程序已退出")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("\n程序已被用户中断")
    except Exception as e:
        logging.error(f"程序异常退出: {str(e)}") 