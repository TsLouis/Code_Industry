"""
Coordinator agent implementation
"""

from typing import Dict, Optional, Any, List
from ..base import BaseAgent, AgentConfig, AgentResponse, Message, AgentRole
from ..utils.llm import LLMTool
from src.core.monitoring.agent_monitor import monitor_agent_action, monitor_conversation


class CoordinatorAgent(BaseAgent):
    """
    Coordinator agent that manages the workflow between different agents.
    Responsible for:
    - Task decomposition and assignment
    - Progress tracking
    - Conflict resolution
    - Quality assurance
    """

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.task_queue: List[Dict[str, Any]] = []
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        # 初始化LLM工具
        self.llm_tool = LLMTool(config.llm_config["adapter"])

    @monitor_agent_action("process_task")
    @monitor_conversation()
    async def process(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process incoming messages and coordinate responses"""
        if not message:
            raise ValueError("Message cannot be empty")

        try:
            # 分析任务
            task_analysis = await self._analyze_task(message)
            # 分配角色
            role_assignments = await self._assign_roles(task_analysis)
            # 创建工作流
            workflow = await self._create_workflow(role_assignments)
            # 监控进度
            progress = await self._monitor_progress(workflow)

            return AgentResponse(
                response="Task has been coordinated",
                metadata={
                    "task_analysis": task_analysis,
                    "role_assignments": role_assignments,
                    "workflow": workflow,
                    "progress": progress
                }
            )
        except Exception as e:
            return AgentResponse(
                response="Error occurred during coordination",
                error=str(e)
            )

    async def plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Create a plan for task execution"""
        if not task:
            raise ValueError("Task cannot be empty")

        try:
            # 分析任务
            task_analysis = await self._analyze_task(task)
            # 分配角色
            role_assignments = await self._assign_roles(task_analysis)
            # 创建工作流
            workflow = await self._create_workflow(role_assignments)
            
            return AgentResponse(
                response="Coordination plan created",
                metadata={
                    "task_analysis": task_analysis,
                    "role_assignments": role_assignments,
                    "workflow": workflow
                }
            )
        except Exception as e:
            return AgentResponse(
                response="Error occurred during planning",
                error=str(e)
            )

    async def execute(self, plan: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Execute the coordination plan"""
        if not plan:
            raise ValueError("Plan cannot be empty")

        try:
            # 监控进度
            progress = await self._monitor_progress({"plan": plan})
            
            return AgentResponse(
                response="Coordination started",
                metadata={
                    "progress": progress,
                    "status": "in_progress"
                }
            )
        except Exception as e:
            return AgentResponse(
                response="Error occurred during execution",
                error=str(e)
            )

    @monitor_agent_action("analyze_task")
    async def _analyze_task(self, task: str) -> Dict[str, Any]:
        """Analyze task and create task analysis"""
        prompt = f"""
        作为一个项目协调者，请分析以下任务并提供详细的分析：
        任务：{task}
        
        请提供：
        1. 任务类型
        2. 所需角色
        3. 工作流程
        4. 时间估计
        5. 风险评估
        
        以JSON格式返回分析结果。
        """
        
        response = await self.llm_tool.aask(prompt)
        return response

    @monitor_agent_action("assign_roles")
    async def _assign_roles(self, task_analysis: Dict[str, Any]) -> List[str]:
        """Assign roles based on task analysis"""
        prompt = f"""
        基于以下任务分析，请分配合适的角色：
        
        分析：{task_analysis}
        
        可用角色：
        - 产品经理（需求分析、功能规划）
        - 开发工程师（代码实现、测试）
        
        请返回角色列表。
        """
        
        response = await self.llm_tool.aask(prompt)
        return response

    @monitor_agent_action("create_workflow")
    async def _create_workflow(self, role_assignments: List[str]) -> Dict[str, Any]:
        """Create workflow based on role assignments"""
        prompt = f"""
        基于以下角色分配，创建工作流程：
        
        角色：{role_assignments}
        
        请提供：
        1. 工作流类型
        2. 步骤列表
        3. 依赖关系
        4. 时间节点
        
        以JSON格式返回工作流。
        """
        
        response = await self.llm_tool.aask(prompt)
        return response

    @monitor_agent_action("monitor_progress")
    async def _monitor_progress(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor progress of workflow execution"""
        prompt = f"""
        请监控以下工作流的执行进度：
        
        工作流：{workflow}
        
        请提供：
        1. 当前状态
        2. 完成度
        3. 下一步行动
        4. 风险提示
        
        以JSON格式返回监控结果。
        """
        
        response = await self.llm_tool.aask(prompt)
        return response 