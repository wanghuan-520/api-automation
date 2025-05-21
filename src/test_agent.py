from typing import Optional
from dataclasses import dataclass
import logging

@dataclass
class TestAgentState:
    """Test agent state representation"""
    message: Optional[str] = None

class TestAgent:
    """Python implementation of TestGAgent"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.state = TestAgentState()
        self.logger = logging.getLogger(__name__)
    
    async def get_description(self) -> str:
        """Get agent description"""
        return "This is a test GAgent for demonstration"
    
    async def get_message(self) -> str:
        """Get current message"""
        return self.state.message or ""
    
    async def set_message(self, message: str) -> None:
        """Set new message"""
        self.state.message = message
        self.logger.info(f"Message set to: {message}")
    
    async def handle_event(self, message: str) -> None:
        """Handle incoming event"""
        self.logger.info(f"Received message: {message}")
        await self.set_message(message) 