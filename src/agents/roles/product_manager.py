"""
Product Manager agent implementation
"""

from typing import Dict, List, Any, Optional
from ..base import BaseAgent, AgentConfig, AgentResponse
from ..base.types import Requirement, Specifications, UserStory
from ..utils.llm import LLMTool
from src.core.monitoring.agent_monitor import monitor_agent_action, monitor_conversation


class ProductManagerAgent(BaseAgent):
    """
    Product Manager agent that handles product requirements and planning.
    Responsible for:
    - Requirements analysis
    - Feature specification
    - User story creation
    - Product roadmap planning
    """

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        if config.llm_config is None:
            config.llm_config = {
                "adapter": "openai",
                "model": "gpt-3.5-turbo"
            }
        self.llm_tool = LLMTool(config.llm_config["adapter"])

    @monitor_agent_action("process")
    @monitor_conversation()
    async def process(self, message: str) -> AgentResponse:
        """处理产品需求"""
        if not message:
            raise ValueError("Message cannot be empty")

        # 分析需求
        requirements = await self._analyze_requirements(message)
        
        # 创建规格说明
        specs = await self._create_specifications(requirements)
        
        # 生成用户故事
        stories = await self._generate_user_stories(specs)
        
        # 创建产品计划
        plan = await self._create_product_plan(stories)
        
        return AgentResponse(
            response="产品需求已分析完成",
            metadata={
                "requirements": requirements,
                "specifications": specs,
                "user_stories": stories,
                "product_plan": plan
            }
        )

    async def plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Create a product development plan"""
        if not task:
            raise ValueError("Task cannot be empty")

        # Analyze requirements
        requirements = await self._analyze_requirements(task)
        # Create specifications
        specs = await self._create_specifications(requirements)
        # Generate user stories
        stories = await self._generate_user_stories(specs)
        # Create product plan
        plan = await self._create_product_plan(stories)

        return AgentResponse(
            response="Product development plan created",
            metadata={
                "requirements": requirements,
                "specifications": specs,
                "user_stories": stories,
                "product_plan": plan
            }
        )

    async def execute(self, plan: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Execute the product development plan"""
        if not plan:
            raise ValueError("Plan cannot be empty")

        # Initialize development
        init_result = await self._initialize_development({"plan": plan})

        return AgentResponse(
            response="Product development initialized",
            metadata={
                "initialization": init_result,
                "status": "started"
            }
        )

    @monitor_agent_action("analyze_requirements")
    async def _analyze_requirements(self, message: str) -> Dict[str, Any]:
        """分析产品需求"""
        prompt = f"""
        作为一个产品经理，请分析以下需求并提供详细的需求列表：
        需求：{message}
        
        请提供：
        1. 功能需求（包括核心玩法、交互方式、游戏规则等）
        2. 非功能需求（性能、可用性、兼容性等）
        3. 用户场景（游戏流程、操作方式等）
        4. 优先级（核心功能、次要功能、可选功能）
        5. 验收标准（完成条件、测试标准等）
        
        对于贪吃蛇游戏，请特别关注：
        - 蛇的移动机制
        - 食物生成规则
        - 碰撞检测
        - 计分系统
        - 游戏难度
        - 用户界面
        
        以JSON格式返回需求列表。
        """
        
        response = await self.llm_tool.aask(prompt)
        return response

    @monitor_agent_action("create_specifications")
    async def _create_specifications(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """创建产品规格说明"""
        prompt = f"""
        基于以下需求列表，创建详细的产品规格说明：
        
        需求：{requirements}
        
        请提供：
        1. 功能规格
           - 游戏核心机制
           - 控制方式
           - 界面布局
           - 计分规则
           - 难度设置
        
        2. 技术规格
           - 开发语言和框架
           - 性能要求
           - 兼容性要求
           
        3. 界面规格
           - 窗口大小
           - 颜色方案
           - 字体设置
           - 动画效果
           
        4. 交互规格
           - 按键映射
           - 响应时间
           - 反馈方式
           
        5. 测试规格
           - 功能测试点
           - 性能测试点
           - 兼容性测试点
        
        以JSON格式返回规格说明。
        """
        
        response = await self.llm_tool.aask(prompt)
        return response

    @monitor_agent_action("generate_user_stories")
    async def _generate_user_stories(self, specs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成用户故事"""
        prompt = f"""
        基于以下产品规格，生成用户故事：
        
        规格：{specs}
        
        请为以下场景生成用户故事：
        1. 游戏开始
        2. 蛇的移动
        3. 食物收集
        4. 分数计算
        5. 游戏结束
        
        每个用户故事应包含：
        1. 角色（谁）
        2. 目标（想要做什么）
        3. 原因（为什么）
        4. 验收标准（如何验证）
        
        以JSON格式返回用户故事列表。
        """
        
        response = await self.llm_tool.aask(prompt)
        return response

    @monitor_agent_action("create_product_plan")
    async def _create_product_plan(self, stories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """创建产品开发计划"""
        prompt = f"""
        基于以下用户故事，创建产品开发计划：
        
        用户故事：{stories}
        
        请提供：
        1. 开发阶段
           - 核心功能实现
           - 界面开发
           - 测试和优化
           
        2. 时间估算
           - 每个阶段的预计时间
           - 关键节点
           
        3. 优先级排序
           - 必须实现的功能
           - 重要但非必须的功能
           - 可选增强功能
           
        4. 风险评估
           - 技术风险
           - 时间风险
           - 质量风险
           
        5. 验收标准
           - 功能完整性
           - 性能指标
           - 用户体验
        
        以JSON格式返回开发计划。
        """
        
        response = await self.llm_tool.aask(prompt)
        return response

    @monitor_agent_action("initialize_development")
    async def _initialize_development(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize development process"""
        if not plan:
            raise ValueError("Plan cannot be empty")

        prompt = f"""
        基于以下开发计划，初始化开发流程：
        
        计划：{plan}
        
        请提供：
        1. 初始化状态
        2. 下一步行动
        3. 团队分工
        4. 关键节点
        
        以JSON格式返回初始化结果。
        """
        
        response = await self.llm_tool.aask(prompt)
        return response 