"""Test cases for base agent interface"""
import pytest
from typing import Dict, Optional, Any
from unittest.mock import AsyncMock, patch
from src.agents.base.interface import BaseAgent
from src.agents.base.types import AgentConfig, AgentResponse, AgentRole


@pytest.fixture
def agent_config() -> AgentConfig:
    """Create a test agent config"""
    return AgentConfig(
        role=AgentRole.DEVELOPER,
        llm_config={
            "adapter": "openai",
            "model": "gpt-4",
            "api_key": "test-key"
        }
    )


class TestAgent(BaseAgent):
    """Test implementation of BaseAgent"""
    async def process(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        if not message:
            raise ValueError("Message cannot be empty")
        return AgentResponse(response="Test response")
    
    async def plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        if not task:
            raise ValueError("Task cannot be empty")
        return AgentResponse(response="Test plan")
    
    async def execute(self, plan: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        if not plan:
            raise ValueError("Plan cannot be empty")
        return AgentResponse(response="Test execution")


@pytest.fixture
def agent(agent_config: AgentConfig) -> TestAgent:
    """Create a test agent instance"""
    return TestAgent(agent_config)


@pytest.mark.asyncio
async def test_process(agent: TestAgent):
    """Test process method"""
    response = await agent.process("Test message")
    assert isinstance(response, AgentResponse)
    assert response.response == "Test response"


@pytest.mark.asyncio
async def test_plan(agent: TestAgent):
    """Test plan method"""
    response = await agent.plan("Test task")
    assert isinstance(response, AgentResponse)
    assert response.response == "Test plan"


@pytest.mark.asyncio
async def test_execute(agent: TestAgent):
    """Test execute method"""
    response = await agent.execute("Test plan")
    assert isinstance(response, AgentResponse)
    assert response.response == "Test execution"


@pytest.mark.asyncio
async def test_invalid_process(agent_config: AgentConfig):
    """Test process with invalid config"""
    agent = TestAgent(agent_config)
    with pytest.raises(ValueError, match="Message cannot be empty"):
        await agent.process("")


@pytest.mark.asyncio
async def test_invalid_plan(agent_config: AgentConfig):
    """Test plan with invalid task"""
    agent = TestAgent(agent_config)
    with pytest.raises(ValueError, match="Task cannot be empty"):
        await agent.plan("")


@pytest.mark.asyncio
async def test_invalid_execute(agent_config: AgentConfig):
    """Test execute with invalid task"""
    agent = TestAgent(agent_config)
    with pytest.raises(ValueError, match="Plan cannot be empty"):
        await agent.execute("") 