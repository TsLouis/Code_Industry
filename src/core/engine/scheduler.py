"""
任务调度器模块
负责任务的调度和执行管理
"""

import asyncio
from typing import Any, Dict, List, Optional, Set
from datetime import datetime
from .task import Task, TaskStatus, TaskPriority

class Scheduler:
    """任务调度器"""
    
    def __init__(self, max_concurrent_tasks: int = 5):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.running_tasks: Set[str] = set()
        self.task_queue: List[Task] = []
        self._stop = False
        
    async def start(self):
        """启动调度器"""
        self._stop = False
        while not self._stop:
            await self._process_queue()
            await asyncio.sleep(0.1)  # 避免过度消耗CPU
            
    async def stop(self):
        """停止调度器"""
        self._stop = True
        
    def schedule_task(self, task: Task):
        """调度任务"""
        # 根据优先级插入队列
        insert_pos = 0
        for i, queued_task in enumerate(self.task_queue):
            if queued_task.priority.value < task.priority.value:
                insert_pos = i
                break
            insert_pos = i + 1
        self.task_queue.insert(insert_pos, task)
        
    async def _process_queue(self):
        """处理任务队列"""
        if len(self.running_tasks) >= self.max_concurrent_tasks:
            return
            
        # 获取可以执行的任务数量
        available_slots = self.max_concurrent_tasks - len(self.running_tasks)
        
        # 从队列中获取任务执行
        tasks_to_run = []
        while available_slots > 0 and self.task_queue:
            task = self.task_queue.pop(0)
            if task.status == TaskStatus.PENDING:
                tasks_to_run.append(task)
                available_slots -= 1
                
        # 执行任务
        for task in tasks_to_run:
            asyncio.create_task(self._execute_task(task))
            
    async def _execute_task(self, task: Task):
        """执行任务"""
        try:
            # 标记任务开始执行
            task.status = TaskStatus.EXECUTING
            task.started_at = datetime.now()
            self.running_tasks.add(task.task_id)
            
            # 执行任务的每个步骤
            for step in task.steps:
                step.status = TaskStatus.EXECUTING
                step.start_time = datetime.now()
                
                try:
                    # TODO: 实现具体的步骤执行逻辑
                    # result = await execute_step(step)
                    # step.result = result
                    step.status = TaskStatus.COMPLETED
                except Exception as e:
                    step.status = TaskStatus.FAILED
                    step.error = str(e)
                    raise
                    
                step.end_time = datetime.now()
                
            # 标记任务完成
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
        except Exception as e:
            # 处理任务执行错误
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            
        finally:
            # 清理任务状态
            self.running_tasks.remove(task.task_id)
            
    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态"""
        return {
            "queue_length": len(self.task_queue),
            "running_tasks": len(self.running_tasks),
            "available_slots": self.max_concurrent_tasks - len(self.running_tasks)
        }
        
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """获取任务状态"""
        # 检查运行中的任务
        if task_id in self.running_tasks:
            return TaskStatus.EXECUTING
            
        # 检查队列中的任务
        for task in self.task_queue:
            if task.task_id == task_id:
                return task.status
                
        return None 