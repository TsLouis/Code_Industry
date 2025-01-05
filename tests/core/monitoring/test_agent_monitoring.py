"""
Agent监控模块的测试用例
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

from src.core.comms.types import Message
from src.agents.base.agent import BaseAgent, ProductManagerAgent, DeveloperAgent, ReviewerAgent
from src.core.monitoring.agent_monitor import agent_monitor, monitor_agent_action

@dataclass
class TestMessage:
    """测试用消息类"""
    id: str
    type: str
    sender: str
    receiver: str
    content: Dict[str, Any]
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class MockProductManagerAgent(ProductManagerAgent):
    """模拟产品经理Agent"""
    
    @monitor_agent_action("analyze_requirement")
    async def analyze_requirement(self, requirement: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(requirement, dict) or not requirement.get("feature"):
            raise ValueError("Invalid requirement: must be a dictionary with a 'feature' field")
            
        await asyncio.sleep(0.1)  # 模拟处理时间
        return {
            "status": "analyzed",
            "priority": "high",
            "complexity": "medium",
            "estimated_time": "2 days"
        }
        
    @monitor_agent_action("create_task")
    async def create_task(self, requirement: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.1)  # 模拟处理时间
        return {
            "task_id": "task-001",
            "title": "实现新功能",
            "description": "详细的任务描述",
            "assignee": "developer-001"
        }

class MockDeveloperAgent(DeveloperAgent):
    """模拟开发者Agent"""
    
    @monitor_agent_action("implement_feature")
    async def implement_feature(self, task: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.2)  # 模拟处理时间
        return {
            "status": "completed",
            "code": "print('Hello, World!')",
            "tests": ["test_case_1", "test_case_2"]
        }
        
    @monitor_agent_action("review_code")
    async def review_code(self, code: str) -> list[str]:
        await asyncio.sleep(0.1)  # 模拟处理时间
        return [
            "代码符合规范",
            "性能良好",
            "建议添加更多注释"
        ]

@pytest.fixture
async def setup_agents() -> Tuple[MockProductManagerAgent, MockDeveloperAgent, ReviewerAgent]:
    """设置测试用的agents"""
    pm = MockProductManagerAgent("pm-001")
    dev = MockDeveloperAgent("dev-001")
    reviewer = ReviewerAgent("reviewer-001")
    
    await pm.initialize()
    await dev.initialize()
    await reviewer.initialize()
    
    return pm, dev, reviewer

@pytest.mark.asyncio
async def test_agent_actions(setup_agents: Tuple[MockProductManagerAgent, MockDeveloperAgent, ReviewerAgent]):
    """测试Agent行为监控"""
    pm, dev, _ = setup_agents
    
    # 测试产品经理的行为
    requirement = {
        "feature": "新功能",
        "description": "详细描述",
        "priority": "high"
    }
    
    analysis = await pm.analyze_requirement(requirement)
    assert analysis["status"] == "analyzed"
    
    task = await pm.create_task(requirement)
    assert task["task_id"] == "task-001"
    
    # 测试开发者的行为
    implementation = await dev.implement_feature(task)
    assert implementation["status"] == "completed"
    
    review_results = await dev.review_code(implementation["code"])
    assert len(review_results) == 3
    
    # 验证监控记录
    pm_actions = agent_monitor.get_agent_actions(str(id(pm)))
    assert len(pm_actions) > 0
    assert any(a.action_type == "analyze_requirement" for a in pm_actions)
    
    dev_actions = agent_monitor.get_agent_actions(str(id(dev)))
    assert len(dev_actions) > 0
    assert any(a.action_type == "implement_feature" for a in dev_actions)

@pytest.mark.asyncio
async def test_agent_conversations(setup_agents: Tuple[MockProductManagerAgent, MockDeveloperAgent, ReviewerAgent]):
    """测试Agent对话监控"""
    pm, dev, _ = setup_agents
    
    # 创建测试消息
    message = TestMessage(
        id="msg-001",
        type="task_assignment",
        sender=str(id(pm)),
        receiver=str(id(dev)),
        content={"task": "实现新功能"}
    )
    
    # 发送消息
    await pm.send_message(message)
    
    # 处理消息
    await dev.process_message(message)
    
    # 验证对话记录
    conversations = agent_monitor.get_agent_conversations(str(id(pm)))
    assert len(conversations) > 0
    assert any(c.sender == str(id(pm)) for c in conversations)
    
    dev_conversations = agent_monitor.get_agent_conversations(str(id(dev)))
    assert len(dev_conversations) > 0
    assert any(c.receiver == str(id(dev)) for c in dev_conversations)

@pytest.mark.asyncio
async def test_thought_process_monitoring(setup_agents: Tuple[MockProductManagerAgent, MockDeveloperAgent, ReviewerAgent]):
    """测试思考过程监控"""
    pm, _, _ = setup_agents
    
    requirement = {
        "feature": "新功能",
        "description": "详细描述",
        "priority": "high"
    }
    
    # 执行需要思考的操作
    await pm.analyze_requirement(requirement)
    
    # 验证思考过程记录
    thoughts = agent_monitor.get_agent_thought_process(str(id(pm)))
    assert len(thoughts) > 0
    assert "分析当前需求和上下文" in thoughts[0]["thought_process"]

@pytest.mark.asyncio
async def test_performance_monitoring(setup_agents: Tuple[MockProductManagerAgent, MockDeveloperAgent, ReviewerAgent]):
    """测试性能监控"""
    pm, _, _ = setup_agents
    
    requirement = {
        "feature": "新功能",
        "description": "详细描述",
        "priority": "high"
    }
    
    # 执行多次操作以生成性能数据
    for _ in range(3):
        await pm.analyze_requirement(requirement)
        await pm.create_task(requirement)
    
    # 获取性能统计
    performance = agent_monitor.get_agent_performance(str(id(pm)))
    
    # 验证性能数据
    assert "analyze_requirement" in performance
    assert "create_task" in performance
    assert performance["analyze_requirement"]["count"] == 3
    assert performance["create_task"]["count"] == 3
    assert "avg_duration" in performance["analyze_requirement"]
    assert "min_duration" in performance["analyze_requirement"]
    assert "max_duration" in performance["analyze_requirement"]

@pytest.mark.asyncio
async def test_error_handling_monitoring(setup_agents: Tuple[MockProductManagerAgent, MockDeveloperAgent, ReviewerAgent]):
    """测试错误处理监控"""
    pm, _, _ = setup_agents
    
    # 触发一个错误
    with pytest.raises(ValueError):
        await pm.analyze_requirement({"invalid": None})  # 触发错误
    
    # 验证错误记录
    actions = agent_monitor.get_agent_actions(str(id(pm)))
    error_actions = [a for a in actions if a.action_type == "analyze_requirement_error"]
    assert len(error_actions) > 0

@pytest.mark.asyncio
async def test_state_monitoring(setup_agents: Tuple[MockProductManagerAgent, MockDeveloperAgent, ReviewerAgent]):
    """测试状态监控"""
    pm, _, _ = setup_agents
    
    # 更新状态
    await pm.update_state({
        "current_task": "task-001",
        "status": "working"
    })
    
    # 验证状态更新记录
    actions = agent_monitor.get_agent_actions(str(id(pm)))
    state_updates = [a for a in actions if a.action_type == "update_state"]
    assert len(state_updates) > 0

if __name__ == "__main__":
    pytest.main([__file__]) 