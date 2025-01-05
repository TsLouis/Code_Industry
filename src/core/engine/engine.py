"""
引擎核心模块
负责协调各个组件完成任务处理流程
"""

import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

from src.core.monitoring import monitor, metrics
from src.core.comms import broker, types
from src.agents.base import agent
from src.agents.roles.coordinator import CoordinatorAgent
from src.agents.roles.product_manager import ProductManagerAgent
from src.agents.roles.developer import DeveloperAgent
from src.adapters.base.types import ModelProvider

@dataclass
class TaskConfig:
    """任务配置"""
    max_steps: int = 10
    timeout: float = 300.0  # 秒
    allow_parallel: bool = True

@dataclass
class TaskContext:
    """任务上下文"""
    task_id: str
    user_input: str
    start_time: datetime
    config: TaskConfig
    state: Dict[str, Any] = None
    history: List[Dict[str, Any]] = None

class Engine:
    """引擎核心类"""
    
    def __init__(self):
        self.message_broker = None
        self.active_tasks = {}
        self.monitor = monitor.Monitor()
        
        # 初始化核心Agent的默认配置
        from src.adapters.providers.openai import OpenAIAdapter, create_openai_config
        from src.config import get_openai_api_key, LLM_CONFIG
        
        config = create_openai_config(
            api_key=get_openai_api_key(),
            model_name=LLM_CONFIG["model"],
            temperature=LLM_CONFIG["temperature"],
            max_tokens=LLM_CONFIG["max_tokens"],
            base_url=LLM_CONFIG["base_url"]
        )
        adapter = OpenAIAdapter(config)
        default_config = agent.AgentConfig(llm_config={"adapter": adapter})
        
        # 初始化核心Agent
        self.coordinator = CoordinatorAgent(config=default_config)
        self.product_manager = ProductManagerAgent(config=default_config)
        self.developer = DeveloperAgent(config=default_config)
        
    async def initialize(self):
        """异步初始化"""
        self.message_broker = await broker.MessageBroker.create()
        return self
        
    async def process_input(self, user_input: str, task_config: Optional[TaskConfig] = None) -> Dict[str, Any]:
        """处理用户输入"""
        if task_config is None:
            task_config = TaskConfig()
            
        # 创建任务上下文
        timestamp = datetime.now()
        task_id = f"task_{timestamp.strftime('%Y%m%d_%H%M%S')}_{timestamp.microsecond}"
        context = TaskContext(
            task_id=task_id,
            user_input=user_input,
            start_time=timestamp,
            config=task_config,
            state={},
            history=[]
        )
        
        try:
            # 记录任务开始
            self.monitor.log_operation(
                "task_start",
                "started",
                context={"task_id": task_id, "input": user_input}
            )
            
            # 初始化任务
            self.active_tasks[task_id] = context
            
            # 任务处理流程
            result = await self._execute_task(context)
            
            # 记录任务完成
            self.monitor.log_operation(
                "task_complete",
                "success",
                context={"task_id": task_id, "result": result}
            )
            
            # 确保结果包含任务ID
            result["task_id"] = task_id
            
            return result
            
        except Exception as e:
            # 记录错误
            self.monitor.log_error(
                "task_error",
                e,
                context={"task_id": task_id}
            )
            raise
            
        finally:
            # 清理任务
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
                
    async def _execute_task(self, context: TaskContext) -> Dict[str, Any]:
        """执行任务处理流程"""
        # 1. 任务分析
        task_spec = await self._analyze_task(context)
        
        # 2. 创建执行计划
        plan = await self._create_execution_plan(task_spec)
        
        # 3. 执行计划
        result = await self._execute_plan(plan, context)
        
        # 4. 整合结果
        final_result = await self._integrate_results(result, context)
        
        return final_result
        
    async def _analyze_task(self, context: TaskContext) -> Dict[str, Any]:
        """分析任务，确定需要的Agent和执行步骤"""
        # 使用协调者Agent分析任务
        analysis_message = self._create_task_message(
            "task_analysis",
            {
                "input": context.user_input,
                "task_id": context.task_id
            }
        )
        
        # 发送给协调者进行分析
        analysis_result = await self.coordinator.process(analysis_message.content)
        
        # 将 AgentResponse 转换为字典
        result_dict = {
            "content": analysis_result.response,
            "role": analysis_result.messages[0].role if analysis_result.messages else "assistant",
            "model": "gpt-3.5-turbo",
            "usage": analysis_result.metadata.get("usage", {}) if analysis_result.metadata else {}
        }
        
        # 记录分析结果
        context.state["analysis"] = result_dict
        context.state["coordinator_process"] = result_dict
        context.history.append({
            "stage": "analysis",
            "result": result_dict,
            "timestamp": datetime.now()
        })
        
        return result_dict
        
    async def _create_execution_plan(self, task_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建任务执行计划"""
        # 根据任务规格创建执行计划
        plan = []
        
        # 1. 产品需求分析
        if task_spec.get("needs_requirements_analysis", True):
            plan.append({
                "agent": "product_manager",
                "action": "analyze_requirements",
                "parameters": task_spec
            })
            
        # 2. 技术方案设计
        if task_spec.get("needs_technical_design", True):
            plan.append({
                "agent": "developer",
                "action": "create_technical_design",
                "parameters": task_spec
            })
            
        # 3. 实现步骤
        if task_spec.get("needs_implementation", True):
            plan.append({
                "agent": "developer",
                "action": "implement",
                "parameters": task_spec
            })
            
        # 4. 测试验证
        if task_spec.get("needs_testing", True):
            plan.append({
                "agent": "developer",
                "action": "test",
                "parameters": task_spec
            })
            
        return plan
        
    async def _execute_plan(self, plan: List[Dict[str, Any]], context: TaskContext) -> List[Dict[str, Any]]:
        """执行计划"""
        results = []
        
        for step in plan:
            try:
                # 获取对应的Agent
                agent_instance = self._get_agent_for_step(step["agent"])
                
                # 创建步骤消息
                step_message = self._create_task_message(
                    step["action"],
                    {
                        "parameters": step["parameters"],
                        "context": context.state,
                        "task_id": context.task_id
                    }
                )
                
                # 执行步骤
                step_result = await agent_instance.process(step_message.content)
                
                # 将 AgentResponse 转换为字典
                result_dict = {
                    "content": step_result.response,
                    "role": step_result.messages[0].role if step_result.messages else "assistant",
                    "model": "gpt-3.5-turbo",
                    "usage": step_result.metadata.get("usage", {}) if step_result.metadata else {}
                }
                
                # 记录结果
                results.append({
                    "step": step,
                    "result": result_dict,
                    "status": "success"
                })
                
                # 更新上下文状态
                context.state[f"{step['agent']}_{step['action']}"] = result_dict
                context.history.append({
                    "stage": f"{step['agent']}_{step['action']}",
                    "result": result_dict,
                    "timestamp": datetime.now()
                })
                
            except Exception as e:
                # 记录错误
                error_result = {
                    "step": step,
                    "error": str(e),
                    "status": "failed"
                }
                results.append(error_result)
                context.history.append({
                    "stage": f"{step['agent']}_{step['action']}",
                    "error": str(e),
                    "timestamp": datetime.now()
                })
                
                # 根据配置决定是否继续执行
                if not context.config.allow_parallel:
                    break
                    
        return results
        
    async def _integrate_results(self, results: List[Dict[str, Any]], context: TaskContext) -> Dict[str, Any]:
        """整合执行结果"""
        # 分析执行结果
        success_steps = [r for r in results if r["status"] == "success"]
        failed_steps = [r for r in results if r["status"] == "failed"]
        
        # 整合成功步骤的结果
        integrated_result = {
            "task_id": context.task_id,
            "input": context.user_input,
            "execution_time": (datetime.now() - context.start_time).total_seconds(),
            "success_count": len(success_steps),
            "failure_count": len(failed_steps),
            "results": {
                **{
                    f"{r['step']['agent']}_{r['step']['action']}": r['result']
                    for r in success_steps
                },
                **context.state  # 添加上下文状态
            },
            "errors": {
                f"{r['step']['agent']}_{r['step']['action']}": r['error']
                for r in failed_steps
            },
            "status": "completed" if not failed_steps else "partial_success",
            "history": context.history
        }
        
        return integrated_result
        
    def _get_agent_for_step(self, agent_type: str) -> agent.BaseAgent:
        """获取步骤对应的Agent实例"""
        agents = {
            "coordinator": self.coordinator,
            "product_manager": self.product_manager,
            "developer": self.developer
        }
        return agents.get(agent_type)
        
    def _create_task_message(self, task_type: str, content: Dict[str, Any]) -> types.Message:
        """创建任务消息"""
        return types.Message(
            id=f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            type=types.MessageType.TASK,
            content=content,
            sender="engine",
            receiver="coordinator",
            trace_id=content.get("task_id", ""),
            timestamp=datetime.now()
        ) 