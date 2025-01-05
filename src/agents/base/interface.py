"""
Base interface for agents
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from .types import AgentConfig, AgentResponse, Message


class BaseAgent(ABC):
    """Base class for all agents"""

    def __init__(self, config: AgentConfig):
        """Initialize the agent with configuration

        Args:
            config: Agent configuration
        """
        self.config = config
        self.conversation_history: List[Message] = []

    @abstractmethod
    async def process(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process a message and return a response

        Args:
            message: Input message to process
            context: Optional context information

        Returns:
            Agent's response
        """
        pass

    @abstractmethod
    async def plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Plan how to accomplish a task

        Args:
            task: Task description
            context: Optional context information

        Returns:
            Planning response with steps
        """
        pass

    @abstractmethod
    async def execute(self, plan: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Execute a plan

        Args:
            plan: Plan to execute
            context: Optional context information

        Returns:
            Execution results
        """
        pass

    def add_message(self, message: Message) -> None:
        """Add a message to conversation history

        Args:
            message: Message to add
        """
        self.conversation_history.append(message)

    def clear_history(self) -> None:
        """Clear conversation history"""
        self.conversation_history.clear()

    @property
    def name(self) -> str:
        """Get agent name"""
        return self.config.name

    @property
    def role(self) -> str:
        """Get agent role"""
        return self.config.role

    @property
    def description(self) -> str:
        """Get agent description"""
        return self.config.description 