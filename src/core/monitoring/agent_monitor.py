"""
Agent监控模块
用于跟踪和分析Agent的行为、决策过程和性能
"""

import functools
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from .monitor import monitor

@dataclass
class AgentAction:
    """Agent行为记录"""
    agent_id: str
    agent_type: str
    action_type: str
    timestamp: datetime
    context: Dict[str, Any]
    duration: float
    result: Optional[Any] = None
    thought_process: Optional[str] = None
    
@dataclass
class AgentConversation:
    """Agent对话记录"""
    conversation_id: str
    timestamp: datetime
    sender: str
    receiver: str
    message: str
    context: Dict[str, Any]

class AgentMonitor:
    """Agent监控器"""
    
    def __init__(self):
        self.actions: List[AgentAction] = []
        self.conversations: List[AgentConversation] = []
        
    def record_action(self, action: AgentAction):
        """记录Agent行为"""
        self.actions.append(action)
        # 记录到监控系统
        monitor.log_operation(
            operation=f"agent_{action.action_type}",
            status="success",
            context={
                "agent_id": action.agent_id,
                "agent_type": action.agent_type,
                "duration": action.duration,
                "thought_process": action.thought_process
            }
        )
        
    def record_conversation(self, conversation: AgentConversation):
        """记录Agent对话"""
        self.conversations.append(conversation)
        # 记录到监控系统
        monitor.log_operation(
            operation="agent_conversation",
            status="success",
            context={
                "conversation_id": conversation.conversation_id,
                "sender": conversation.sender,
                "receiver": conversation.receiver,
                "timestamp": conversation.timestamp.isoformat()
            }
        )
        
    def get_agent_actions(self, agent_id: str) -> List[AgentAction]:
        """获取指定Agent的所有行为记录"""
        return [action for action in self.actions if action.agent_id == agent_id]
        
    def get_agent_conversations(self, agent_id: str) -> List[AgentConversation]:
        """获取指定Agent的所有对话记录"""
        return [
            conv for conv in self.conversations 
            if conv.sender == agent_id or conv.receiver == agent_id
        ]
        
    def get_agent_performance(self, agent_id: str) -> Dict[str, Any]:
        """获取Agent的性能统计"""
        actions = self.get_agent_actions(agent_id)
        if not actions:
            return {}
            
        action_times = {}
        action_counts = {}
        
        for action in actions:
            if action.action_type not in action_times:
                action_times[action.action_type] = []
                action_counts[action.action_type] = 0
                
            action_times[action.action_type].append(action.duration)
            action_counts[action.action_type] += 1
            
        performance = {}
        for action_type in action_times:
            times = action_times[action_type]
            performance[action_type] = {
                "count": action_counts[action_type],
                "avg_duration": sum(times) / len(times),
                "min_duration": min(times),
                "max_duration": max(times)
            }
            
        return performance
        
    def get_agent_thought_process(self, agent_id: str) -> List[Dict[str, Any]]:
        """获取Agent的思考过程记录"""
        thoughts = []
        for action in self.get_agent_actions(agent_id):
            if action.thought_process:
                thoughts.append({
                    "timestamp": action.timestamp,
                    "action_type": action.action_type,
                    "thought_process": action.thought_process,
                    "context": action.context
                })
        return thoughts

# 创建全局Agent监控器实例
agent_monitor = AgentMonitor()

def monitor_agent_action(action_type: str):
    """监控Agent行为的装饰器"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            start_time = time.time()
            context = {
                "args": str(args),
                "kwargs": str(kwargs),
                "method": func.__name__
            }
            
            try:
                # 获取思考过程（如果有）
                thought_process = getattr(self, "thought_process", None)
                if callable(thought_process):
                    context["thought_process"] = await thought_process(*args, **kwargs)
                
                # 执行操作
                result = await func(self, *args, **kwargs)
                
                # 记录行为
                action = AgentAction(
                    agent_id=str(id(self)),
                    agent_type=self.__class__.__name__,
                    action_type=action_type,
                    timestamp=datetime.now(),
                    context=context,
                    duration=time.time() - start_time,
                    result=str(result) if result else None,
                    thought_process=context.get("thought_process")
                )
                agent_monitor.record_action(action)
                
                return result
                
            except Exception as e:
                # 记录错误
                context["error"] = str(e)
                action = AgentAction(
                    agent_id=str(id(self)),
                    agent_type=self.__class__.__name__,
                    action_type=f"{action_type}_error",
                    timestamp=datetime.now(),
                    context=context,
                    duration=time.time() - start_time
                )
                agent_monitor.record_action(action)
                raise
                
        return wrapper
    return decorator

def monitor_conversation():
    """监控Agent对话的装饰器"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            # 提取消息信息
            message = args[0] if args else kwargs.get("message")
            if not message:
                return await func(self, *args, **kwargs)
                
            # 记录对话
            conversation = AgentConversation(
                conversation_id=str(id(message)),
                timestamp=datetime.now(),
                sender=str(id(self)),
                receiver=getattr(message, "receiver", "unknown"),
                message=str(message),
                context={
                    "method": func.__name__,
                    "message_type": getattr(message, "type", None)
                }
            )
            agent_monitor.record_conversation(conversation)
            
            return await func(self, *args, **kwargs)
            
        return wrapper
    return decorator 