"""
引擎模块测试用例
"""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock

from src.core.engine.engine import Engine, TaskConfig, TaskContext
from src.core.comms.types import Message
from src.agents.base.agent import BaseAgent, AgentConfig

class MockAgent(BaseAgent):
    """模拟Agent类"""
    def __init__(self, name: str):
        config = AgentConfig(
            llm_config={
                "adapter": {
                    "model": "mock-model",
                    "temperature": 0.5,
                    "max_tokens": 1000
                }
            }
        )
        super().__init__(agent_id=name, config=config)
        self.name = name
        self.process_calls = []
        
    async def process(self, content: Dict[str, Any]) -> Dict[str, Any]:
        self.process_calls.append(content)
        return {
            "status": "success",
            "agent": self.name,
            "result": f"Processed by {self.name}"
        }

class MockFailingAgent(BaseAgent):
    """模拟失败的Agent类"""
    def __init__(self, name: str):
        config = AgentConfig(
            llm_config={
                "adapter": {
                    "model": "mock-model",
                    "temperature": 0.5,
                    "max_tokens": 1000
                }
            }
        )
        super().__init__(agent_id=name, config=config)
        self.name = name
        
    async def process(self, content: Dict[str, Any]) -> Dict[str, Any]:
        raise Exception(f"Error in {self.name}")

@pytest_asyncio.fixture
async def engine():
    """创建引擎实例"""
    engine = Engine()
    engine = await engine.initialize()
    # 替换为mock agents
    engine.coordinator = MockAgent("coordinator")
    engine.product_manager = MockAgent("product_manager")
    engine.developer = MockAgent("developer")
    return engine

@pytest_asyncio.fixture
async def failing_engine():
    """创建包含失败Agent的引擎实例"""
    engine = Engine()
    engine = await engine.initialize()
    engine.coordinator = MockAgent("coordinator")
    engine.product_manager = MockFailingAgent("product_manager")
    engine.developer = MockAgent("developer")
    return engine

@pytest.mark.asyncio
async def test_basic_task_execution(engine):
    """测试基本任务执行流程"""
    # 执行任务
    result = await engine.process_input("测试任务")
    
    # 验证任务执行结果
    assert result["status"] == "completed"
    assert result["success_count"] > 0
    assert result["failure_count"] == 0
    assert "coordinator_process" in str(result["results"])
    
    # 验证任务历史
    assert len(result["history"]) > 0
    assert result["history"][0]["stage"] == "analysis"

@pytest.mark.asyncio
async def test_task_analysis(engine):
    """测试任务分析功能"""
    context = TaskContext(
        task_id="test_task",
        user_input="测试任务分析",
        start_time=datetime.now(),
        config=TaskConfig(),
        state={},
        history=[]
    )
    
    # 执行任务分析
    analysis_result = await engine._analyze_task(context)
    
    # 验证分析结果
    assert analysis_result is not None
    assert "status" in analysis_result
    assert analysis_result["status"] == "success"
    
    # 验证上下文更新
    assert "analysis" in context.state
    assert len(context.history) == 1
    assert context.history[0]["stage"] == "analysis"

@pytest.mark.asyncio
async def test_execution_plan_creation(engine):
    """测试执行计划创建"""
    task_spec = {
        "needs_requirements_analysis": True,
        "needs_technical_design": True,
        "needs_implementation": True,
        "needs_testing": True
    }
    
    # 创建执行计划
    plan = await engine._create_execution_plan(task_spec)
    
    # 验证计划内容
    assert len(plan) == 4  # 应该包含所有步骤
    assert plan[0]["agent"] == "product_manager"
    assert plan[1]["agent"] == "developer"
    assert plan[2]["agent"] == "developer"
    assert plan[3]["agent"] == "developer"

@pytest.mark.asyncio
async def test_plan_execution(engine):
    """测试计划执行"""
    context = TaskContext(
        task_id="test_task",
        user_input="测试计划执行",
        start_time=datetime.now(),
        config=TaskConfig(),
        state={},
        history=[]
    )
    
    plan = [
        {
            "agent": "product_manager",
            "action": "analyze_requirements",
            "parameters": {}
        },
        {
            "agent": "developer",
            "action": "implement",
            "parameters": {}
        }
    ]
    
    # 执行计划
    results = await engine._execute_plan(plan, context)
    
    # 验证执行结果
    assert len(results) == 2
    assert all(r["status"] == "success" for r in results)
    assert len(context.history) == 2

@pytest.mark.asyncio
async def test_error_handling(failing_engine):
    """测试错误处理"""
    # 执行预期会失败的任务
    result = await failing_engine.process_input("测试错误处理")
    
    # 验证错误处理
    assert result["status"] == "partial_success"
    assert result["failure_count"] > 0
    assert len(result["errors"]) > 0

@pytest.mark.asyncio
async def test_parallel_execution():
    """测试并行执行"""
    engine = Engine()
    engine = await engine.initialize()
    engine.coordinator = MockAgent("coordinator")
    engine.product_manager = MockAgent("product_manager")
    engine.developer = MockAgent("developer")
    
    # 并行执行多个任务
    tasks = [
        engine.process_input(f"并行任务 {i}")
        for i in range(3)
    ]
    
    results = await asyncio.gather(*tasks)
    
    # 验证所有任务都成功完成
    assert len(results) == 3
    assert all(r["status"] == "completed" for r in results)
    assert len({r["task_id"] for r in results}) == 3  # 确保任务ID唯一

@pytest.mark.asyncio
async def test_task_lifecycle(engine):
    """测试任务生命周期"""
    # 1. 开始任务
    task_id = None
    result = await engine.process_input("测试生命周期")
    task_id = result["task_id"]
    
    # 2. 验证任务完成后的清理
    assert task_id not in engine.active_tasks
    
    # 3. 验证任务历史完整性
    history = result["history"]
    stages = [entry["stage"] for entry in history]
    assert "analysis" in stages
    assert len(stages) >= 2  # 至少包含分析和一个执行步骤

@pytest.mark.asyncio
async def test_task_context_management(engine):
    """测试任务上下文管理"""
    context = TaskContext(
        task_id="test_task",
        user_input="测试上下文管理",
        start_time=datetime.now(),
        config=TaskConfig(),
        state={},
        history=[]
    )
    
    # 1. 执行任务分析
    await engine._analyze_task(context)
    assert "analysis" in context.state
    
    # 2. 创建和执行计划
    plan = await engine._create_execution_plan({"needs_requirements_analysis": True})
    await engine._execute_plan(plan, context)
    
    # 3. 验证上下文状态
    assert len(context.history) >= 2
    assert len(context.state) >= 2

@pytest.mark.asyncio
async def test_custom_task_config(engine):
    """测试自定义任务配置"""
    config = TaskConfig(
        max_steps=5,
        timeout=60.0,
        allow_parallel=False
    )
    
    result = await engine.process_input("测试自定义配置", config)
    
    # 验证配置是否影响执行
    assert result["status"] in ["completed", "partial_success"]
    
if __name__ == "__main__":
    pytest.main([__file__]) 