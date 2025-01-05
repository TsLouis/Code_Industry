"""Test cases for agent types"""
import pytest
from src.agents.base.types import AgentRole, AgentConfig, Message, AgentResponse

def test_agent_role():
    """Test AgentRole enum"""
    assert AgentRole.COORDINATOR == "coordinator"
    assert AgentRole.PRODUCT_MANAGER == "product_manager"
    assert AgentRole.DEVELOPER == "developer"
    assert AgentRole.SYSTEM == "system"
    assert AgentRole.USER == "user"

def test_agent_config():
    """Test AgentConfig class"""
    # Test with minimal config
    config = AgentConfig(role="developer")
    assert config.role == "developer"
    assert config.name is None
    assert config.llm_config is None

    # Test with full config
    llm_config = {
        "adapter": "openai",
        "model": "gpt-3.5-turbo"
    }
    config = AgentConfig(
        role="developer",
        name="DevAgent",
        llm_config=llm_config
    )
    assert config.role == "developer"
    assert config.name == "DevAgent"
    assert config.llm_config == llm_config

def test_message():
    """Test Message class"""
    # Test with minimal message
    message = Message(
        role=AgentRole.USER,
        content="Hello"
    )
    assert message.role == AgentRole.USER
    assert message.content == "Hello"
    assert message.metadata is None

    # Test with metadata
    metadata = {"timestamp": "2024-01-04T12:00:00Z"}
    message = Message(
        role=AgentRole.SYSTEM,
        content="System message",
        metadata=metadata
    )
    assert message.role == AgentRole.SYSTEM
    assert message.content == "System message"
    assert message.metadata == metadata

def test_agent_response():
    """Test AgentResponse class"""
    # Test with minimal response
    response = AgentResponse(
        response="Success"
    )
    assert response.response == "Success"
    assert response.status == "completed"
    assert response.metadata is None

    # Test with metadata
    metadata = {
        "execution_time": 1.5,
        "tokens_used": 150
    }
    response = AgentResponse(
        response="Task completed",
        status="success",
        metadata=metadata
    )
    assert response.response == "Task completed"
    assert response.status == "success"
    assert response.metadata == metadata

def test_invalid_agent_config():
    """Test AgentConfig with invalid input"""
    with pytest.raises(ValueError):
        AgentConfig(role="")  # Empty role

    with pytest.raises(ValueError):
        AgentConfig(role="invalid_role")  # Invalid role

def test_invalid_message():
    """Test Message with invalid input"""
    with pytest.raises(ValueError):
        Message(role="invalid_role", content="")  # Invalid role

    with pytest.raises(ValueError):
        Message(role=AgentRole.USER, content="")  # Empty content 