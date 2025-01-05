"""Test cases for LLM utilities"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.agents.utils.llm import generate_response, analyze_intent, calculate_priority


@pytest.mark.asyncio
@patch("src.agents.utils.llm.AsyncOpenAI")
async def test_generate_response(mock_openai):
    """Test response generation"""
    # Setup mock
    mock_client = AsyncMock()
    mock_completion = AsyncMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content="Test response"))]
    mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
    mock_openai.return_value = mock_client

    config = {
        "adapter": "openai",
        "model": "gpt-3.5-turbo"
    }
    response = await generate_response(
        "你好，请介绍一下你自己。",
        config
    )
    assert response == "Test response"
    mock_client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_intent():
    """Test intent analysis"""
    result = await analyze_intent(
        "我需要开发一个用户认证系统"
    )
    assert isinstance(result, dict)
    assert "intent" in result
    assert "confidence" in result
    assert isinstance(result["confidence"], float)
    assert 0 <= result["confidence"] <= 1


@pytest.mark.asyncio
async def test_calculate_priority():
    """Test priority calculation"""
    result = await calculate_priority(
        "实现用户注册功能，这是系统的基础功能"
    )
    assert isinstance(result, dict)
    assert "priority" in result
    assert "urgency" in result
    assert "importance" in result
    assert "dependencies" in result
    assert "complexity" in result
    assert "reason" in result


@pytest.mark.asyncio
async def test_generate_response_with_invalid_config():
    """Test generate response with invalid config"""
    with pytest.raises(ValueError):
        await generate_response("Hello", {})


@pytest.mark.asyncio
async def test_analyze_intent_with_invalid_message():
    """Test analyze intent with invalid message"""
    with pytest.raises(ValueError):
        await analyze_intent("")


@pytest.mark.asyncio
async def test_calculate_priority_with_invalid_task():
    """Test calculate priority with invalid task"""
    with pytest.raises(ValueError):
        await calculate_priority("") 