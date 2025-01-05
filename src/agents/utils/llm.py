"""LLM utility functions"""
from typing import Dict, List, Any, Optional
import json
from openai import AsyncOpenAI
from ...adapters.base import BaseLLMAdapter


class LLMTool:
    """LLM tool for agents"""

    def __init__(self, adapter: BaseLLMAdapter):
        self.adapter = adapter
        self.client = AsyncOpenAI()

    async def generate_response(self, prompt: str, config: Dict[str, Any]) -> str:
        """Generate LLM response"""
        if not prompt or not config:
            raise ValueError("Prompt and config are required")

        if config.get("adapter") != "openai":
            raise ValueError("Only OpenAI adapter is supported")

        response = await self.client.chat.completions.create(
            model=config.get("model", "gpt-3.5-turbo"),
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    async def analyze_intent(self, message: str) -> Dict[str, Any]:
        """Analyze message intent"""
        if not message:
            raise ValueError("Message is required")

        prompt = self._create_intent_prompt(message)
        response = await self.adapter.generate(prompt)
        return self._parse_intent_response(response)

    async def calculate_priority(self, task: str) -> Dict[str, Any]:
        """Calculate task priority"""
        if not task:
            raise ValueError("Task is required")

        prompt = self._create_priority_prompt(task)
        response = await self.adapter.generate(prompt)
        return self._parse_priority_response(response)

    def _create_intent_prompt(self, message: str) -> str:
        """Create intent analysis prompt"""
        return f"""Analyze the intent of the following message:

Message: {message}

Choose one of the following types:
1. task_request - User wants to execute a task
2. status_request - User wants to know current status
3. clarification - User needs more information
4. other - Other types

Return in JSON format with fields:
- type: Intent type (one of the above)
- confidence: Confidence score (0-1)
- details: Detailed explanation

Return JSON only."""

    def _create_priority_prompt(self, task: str) -> str:
        """Create priority analysis prompt"""
        return f"""Analyze the priority of the following task:

Task: {task}

Consider these factors:
1. Urgency: Time sensitivity
2. Importance: Impact on project
3. Dependencies: Other tasks depending on this
4. Complexity: Technical complexity and risk

Return in JSON format with fields:
- priority: Priority level (1-5)
- urgency: Urgency level (high/medium/low)
- importance: Importance level (high/medium/low)
- dependencies: List of dependencies
- complexity: Complexity level (high/medium/low)
- reason: Reasoning for priority

Return JSON only."""

    def _parse_intent_response(self, response: str) -> Dict[str, Any]:
        """Parse intent analysis response"""
        try:
            result = json.loads(response)
            if not all(key in result for key in ["type", "confidence", "details"]):
                raise ValueError("Missing required fields in intent response")
            if result["type"] not in ["task_request", "status_request", "clarification", "other"]:
                raise ValueError("Invalid intent type")
            if not (0 <= result["confidence"] <= 1):
                raise ValueError("Confidence must be between 0 and 1")
            return result
        except Exception as e:
            return {
                "type": "other",
                "confidence": 0.5,
                "details": f"Failed to parse intent: {str(e)}"
            }

    def _parse_priority_response(self, response: str) -> Dict[str, Any]:
        """Parse priority analysis response"""
        try:
            result = json.loads(response)
            required_fields = ["priority", "urgency", "importance", "dependencies", "complexity", "reason"]
            if not all(key in result for key in required_fields):
                raise ValueError("Missing required fields in priority response")
            return result
        except Exception as e:
            return {
                "priority": 3,
                "urgency": "medium",
                "importance": "medium",
                "dependencies": [],
                "complexity": "medium",
                "reason": f"Failed to parse priority: {str(e)}"
            }


# Standalone functions for backward compatibility
async def generate_response(prompt: str, config: Dict[str, Any]) -> str:
    """Generate LLM response"""
    if not prompt or not config:
        raise ValueError("Prompt and config are required")

    if config.get("adapter") != "openai":
        raise ValueError("Only OpenAI adapter is supported")

    client = AsyncOpenAI()
    response = await client.chat.completions.create(
        model=config.get("model", "gpt-3.5-turbo"),
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


async def analyze_intent(message: str) -> Dict[str, Any]:
    """Analyze message intent"""
    if not message:
        raise ValueError("Message is required")

    # TODO: Implement intent analysis
    return {
        "intent": "development",
        "confidence": 0.95
    }


async def calculate_priority(task: str) -> Dict[str, Any]:
    """Calculate task priority"""
    if not task:
        raise ValueError("Task is required")

    # TODO: Implement priority calculation
    return {
        "priority": 4,
        "urgency": "high",
        "importance": "high",
        "dependencies": ["database"],
        "complexity": "medium",
        "reason": "Core functionality"
    } 