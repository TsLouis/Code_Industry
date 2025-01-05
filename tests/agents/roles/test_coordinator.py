"""Test cases for coordinator agent"""
import pytest
from typing import Dict, Any
from unittest.mock import AsyncMock, patch

from src.agents.base.types import AgentConfig, AgentResponse, AgentRole
from src.agents.roles.coordinator import CoordinatorAgent

@pytest.fixture
def config() -> AgentConfig:
    return AgentConfig(
        role=AgentRole.COORDINATOR,
        llm_config={
            "adapter": "openai",
            "model": "gpt-4",
            "api_key": "test-key"
        }
    )

@pytest.fixture
def agent(config: AgentConfig) -> CoordinatorAgent:
    return CoordinatorAgent(config)

@pytest.mark.asyncio
async def test_process_empty_message(agent: CoordinatorAgent):
    with pytest.raises(ValueError, match="Message cannot be empty"):
        await agent.process("")

@pytest.mark.asyncio
async def test_process_valid_message(agent: CoordinatorAgent):
    # Mock internal methods
    agent._analyze_task = AsyncMock(return_value={"task": "test"})
    agent._assign_roles = AsyncMock(return_value=["role1"])
    agent._create_workflow = AsyncMock(return_value={"workflow": "test"})
    agent._monitor_progress = AsyncMock(return_value={"status": "ok"})

    response = await agent.process("Coordinate a new task")
    assert isinstance(response, AgentResponse)
    assert response.response == "Task has been coordinated"
    assert response.metadata["task_analysis"] == {"task": "test"}
    assert response.metadata["role_assignments"] == ["role1"]
    assert response.metadata["workflow"] == {"workflow": "test"}
    assert response.metadata["progress"] == {"status": "ok"}

@pytest.mark.asyncio
async def test_plan_empty_task(agent: CoordinatorAgent):
    with pytest.raises(ValueError, match="Task cannot be empty"):
        await agent.plan("")

@pytest.mark.asyncio
async def test_plan_valid_task(agent: CoordinatorAgent):
    # Mock internal methods
    agent._analyze_task = AsyncMock(return_value={"task": "test"})
    agent._assign_roles = AsyncMock(return_value=["role1"])
    agent._create_workflow = AsyncMock(return_value={"workflow": "test"})

    response = await agent.plan("Create a coordination plan")
    assert isinstance(response, AgentResponse)
    assert response.response == "Coordination plan created"
    assert response.metadata["task_analysis"] == {"task": "test"}
    assert response.metadata["role_assignments"] == ["role1"]
    assert response.metadata["workflow"] == {"workflow": "test"}

@pytest.mark.asyncio
async def test_execute_empty_plan(agent: CoordinatorAgent):
    with pytest.raises(ValueError, match="Plan cannot be empty"):
        await agent.execute("")

@pytest.mark.asyncio
async def test_execute_valid_plan(agent: CoordinatorAgent):
    # Mock internal methods
    agent._monitor_progress = AsyncMock(return_value={"status": "ok"})

    response = await agent.execute("Test plan")
    assert isinstance(response, AgentResponse)
    assert response.response == "Coordination started"
    assert response.metadata["progress"] == {"status": "ok"}
    assert response.metadata["status"] == "in_progress" 