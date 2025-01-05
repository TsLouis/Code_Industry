"""Test cases for developer agent"""
import pytest
from typing import Dict, Any
from unittest.mock import AsyncMock, patch

from src.agents.base.types import AgentConfig, AgentResponse, AgentRole
from src.agents.roles.developer import DeveloperAgent

@pytest.fixture
def config() -> AgentConfig:
    return AgentConfig(
        role=AgentRole.DEVELOPER,
        llm_config={
            "adapter": "openai",
            "model": "gpt-4",
            "api_key": "test-key"
        }
    )

@pytest.fixture
def agent(config: AgentConfig) -> DeveloperAgent:
    return DeveloperAgent(config)

@pytest.mark.asyncio
async def test_process_empty_message(agent: DeveloperAgent):
    with pytest.raises(ValueError, match="Message cannot be empty"):
        await agent.process("")

@pytest.mark.asyncio
async def test_process_valid_message(agent: DeveloperAgent):
    # Mock internal methods
    agent._analyze_code = AsyncMock(return_value={"code": "test"})
    agent._implement_solution = AsyncMock(return_value=["solution1"])
    agent._test_implementation = AsyncMock(return_value={"tests": "pass"})
    agent._review_code = AsyncMock(return_value={"status": "ok"})

    response = await agent.process("Implement a new feature")
    assert isinstance(response, AgentResponse)
    assert response.response == "Code has been implemented"
    assert response.metadata["code_analysis"] == {"code": "test"}
    assert response.metadata["implementation"] == ["solution1"]
    assert response.metadata["test_results"] == {"tests": "pass"}
    assert response.metadata["review"] == {"status": "ok"}

@pytest.mark.asyncio
async def test_plan_empty_task(agent: DeveloperAgent):
    with pytest.raises(ValueError, match="Task cannot be empty"):
        await agent.plan("")

@pytest.mark.asyncio
async def test_plan_valid_task(agent: DeveloperAgent):
    # Mock internal methods
    agent._analyze_code = AsyncMock(return_value={"code": "test"})
    agent._implement_solution = AsyncMock(return_value=["solution1"])
    agent._test_implementation = AsyncMock(return_value={"tests": "pass"})

    response = await agent.plan("Create a development plan")
    assert isinstance(response, AgentResponse)
    assert response.response == "Development plan created"
    assert response.metadata["code_analysis"] == {"code": "test"}
    assert response.metadata["implementation"] == ["solution1"]
    assert response.metadata["test_results"] == {"tests": "pass"}

@pytest.mark.asyncio
async def test_execute_empty_plan(agent: DeveloperAgent):
    with pytest.raises(ValueError, match="Plan cannot be empty"):
        await agent.execute("")

@pytest.mark.asyncio
async def test_execute_valid_plan(agent: DeveloperAgent):
    # Mock internal methods
    agent._review_code = AsyncMock(return_value={"status": "ok"})

    response = await agent.execute("Test plan")
    assert isinstance(response, AgentResponse)
    assert response.response == "Development started"
    assert response.metadata["review"] == {"status": "ok"}
    assert response.metadata["status"] == "in_progress" 