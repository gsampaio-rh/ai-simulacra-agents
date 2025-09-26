"""AI Simulacra Agents - Foundational simulation layer for autonomous generative agents."""

__version__ = "0.1.0"
__author__ = "AI Simulacra Team"
__email__ = "team@example.com"

from .models.agent import Agent
from .models.memory import Memory, MemoryType
from .models.event import Event, EventType

__all__ = [
    "Agent",
    "Memory", 
    "MemoryType",
    "Event",
    "EventType",
]
