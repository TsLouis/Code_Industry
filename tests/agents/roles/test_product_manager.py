"""Test cases for product manager agent"""
import pytest
from typing import Dict, Any
from unittest.mock import AsyncMock, patch

from src.agents.base.types import AgentConfig, AgentResponse, AgentRole
from src.agents.roles.product_manager import ProductManagerAgent

@pytest.fixture
def config() -> AgentConfig:
    return AgentConfig(
        role=AgentRole.PRODUCT_MANAGER,
        llm_config={
            "adapter": "openai",
            "model": "gpt-4",
            "api_key": "test-key"
        }
    )

@pytest.fixture
def agent(config: AgentConfig) -> ProductManagerAgent:
    return ProductManagerAgent(config)

@pytest.mark.asyncio
async def test_process_empty_message(agent: ProductManagerAgent):
    with pytest.raises(ValueError, match="Message cannot be empty"):
        await agent.process("")

@pytest.mark.asyncio
async def test_process_valid_message(agent: ProductManagerAgent):
    # Mock internal methods
    agent._analyze_requirements = AsyncMock(return_value=["req1"])
    agent._create_specifications = AsyncMock(return_value=["spec1"])
    agent._generate_user_stories = AsyncMock(return_value=["story1"])
    agent._create_product_plan = AsyncMock(return_value={"plan": "test"})
    agent._initialize_development = AsyncMock(return_value={"status": "ok"})

    response = await agent.process("Create a new feature")
    assert isinstance(response, AgentResponse)
    assert response.response == "Product requirements have been processed"
    assert response.metadata["requirements"] == ["req1"]
    assert response.metadata["specifications"] == ["spec1"]
    assert response.metadata["user_stories"] == ["story1"]
    assert response.metadata["product_plan"] == {"plan": "test"}
    assert response.metadata["initialization"] == {"status": "ok"}

@pytest.mark.asyncio
async def test_plan_empty_task(agent: ProductManagerAgent):
    with pytest.raises(ValueError, match="Task cannot be empty"):
        await agent.plan("")

@pytest.mark.asyncio
async def test_plan_valid_task(agent: ProductManagerAgent):
    # Mock internal methods
    agent._analyze_requirements = AsyncMock(return_value=["req1"])
    agent._create_specifications = AsyncMock(return_value=["spec1"])
    agent._generate_user_stories = AsyncMock(return_value=["story1"])
    agent._create_product_plan = AsyncMock(return_value={"plan": "test"})

    response = await agent.plan("Create a new feature")
    assert isinstance(response, AgentResponse)
    assert response.response == "Product development plan created"
    assert response.metadata["requirements"] == ["req1"]
    assert response.metadata["specifications"] == ["spec1"]
    assert response.metadata["user_stories"] == ["story1"]
    assert response.metadata["product_plan"] == {"plan": "test"}

@pytest.mark.asyncio
async def test_execute_empty_plan(agent: ProductManagerAgent):
    with pytest.raises(ValueError, match="Plan cannot be empty"):
        await agent.execute("")

@pytest.mark.asyncio
async def test_execute_valid_plan(agent: ProductManagerAgent):
    # Mock internal methods
    agent._initialize_development = AsyncMock(return_value={"status": "ok"})

    response = await agent.execute("Test plan")
    assert isinstance(response, AgentResponse)
    assert response.response == "Product development initialized"
    assert response.metadata["initialization"] == {"status": "ok"}
    assert response.metadata["status"] == "started" 