"""
任务管理模块
负责任务的创建、状态管理和生命周期控制
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"       # 等待执行
    ANALYZING = "analyzing"   # 分析中
    PLANNING = "planning"     # 规划中
    EXECUTING = "executing"   # 执行中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"         # 失败
    CANCELLED = "cancelled"   # 已取消

class TaskPriority(Enum):
    """任务优先级"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3

@dataclass
class TaskStep:
    """任务步骤"""
    step_id: str
    agent_type: str
    action: str
    parameters: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

@dataclass
class Task:
    """任务定义"""
    task_id: str
    input: str
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    steps: List[TaskStep] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class TaskManager:
    """任务管理器"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        
    def create_task(self, input: str, priority: TaskPriority = TaskPriority.NORMAL) -> Task:
        """创建新任务"""
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        task = Task(
            task_id=task_id,
            input=input,
            priority=priority,
            status=TaskStatus.PENDING,
            created_at=datetime.now()
        )
        self.tasks[task_id] = task
        return task
        
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self.tasks.get(task_id)
        
    def update_task_status(self, task_id: str, status: TaskStatus, error: Optional[str] = None):
        """更新任务状态"""
        task = self.tasks.get(task_id)
        if task:
            task.status = status
            if status == TaskStatus.FAILED:
                task.error = error
            elif status == TaskStatus.COMPLETED:
                task.completed_at = datetime.now()
                
    def add_task_step(self, task_id: str, agent_type: str, action: str, parameters: Dict[str, Any]) -> Optional[TaskStep]:
        """添加任务步骤"""
        task = self.tasks.get(task_id)
        if task:
            step = TaskStep(
                step_id=f"step_{len(task.steps) + 1}",
                agent_type=agent_type,
                action=action,
                parameters=parameters
            )
            task.steps.append(step)
            return step
        return None
        
    def update_step_status(self, task_id: str, step_id: str, status: TaskStatus, 
                          result: Optional[Dict[str, Any]] = None, 
                          error: Optional[str] = None):
        """更新步骤状态"""
        task = self.tasks.get(task_id)
        if task:
            for step in task.steps:
                if step.step_id == step_id:
                    step.status = status
                    if status == TaskStatus.EXECUTING:
                        step.start_time = datetime.now()
                    elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                        step.end_time = datetime.now()
                    if result:
                        step.result = result
                    if error:
                        step.error = error
                    break
                    
    def get_active_tasks(self) -> List[Task]:
        """获取所有活动任务"""
        return [
            task for task in self.tasks.values()
            if task.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
        ]
        
    def get_task_history(self, task_id: str) -> List[Dict[str, Any]]:
        """获取任务历史"""
        task = self.tasks.get(task_id)
        if not task:
            return []
            
        history = []
        for step in task.steps:
            history.append({
                "step_id": step.step_id,
                "agent_type": step.agent_type,
                "action": step.action,
                "status": step.status.value,
                "start_time": step.start_time,
                "end_time": step.end_time,
                "result": step.result,
                "error": step.error
            })
        return history
        
    def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """清理已完成的任务"""
        current_time = datetime.now()
        for task_id in list(self.tasks.keys()):
            task = self.tasks[task_id]
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                if task.completed_at and (current_time - task.completed_at).total_seconds() > max_age_hours * 3600:
                    del self.tasks[task_id] 