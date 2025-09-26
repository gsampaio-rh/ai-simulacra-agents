"""Event-related data models."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EventType(Enum):
    """Types of events that can occur in the simulation."""
    
    MOVEMENT = "movement"           # Agent moved to a new location
    DIALOGUE = "dialogue"           # Agent spoke to another agent
    ACTION = "action"              # Agent performed an action
    INTERACTION = "interaction"     # Agent interacted with an object
    ENTER = "enter"                # Agent entered a location
    LEAVE = "leave"                # Agent left a location
    SYSTEM = "system"              # System-generated event


class Event(BaseModel):
    """An event that occurs in the simulation world."""
    
    id: UUID = Field(default_factory=uuid4)
    event_type: EventType = Field(..., description="Type of event")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: Optional[str] = Field(
        default=None,
        description="ID of the agent who caused this event"
    )
    location: Optional[str] = Field(
        default=None,
        description="Location where the event occurred"
    )
    content: str = Field(..., description="Description of what happened")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional event parameters"
    )
    observers: List[str] = Field(
        default_factory=list,
        description="Agent IDs who can perceive this event"
    )
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class ActionEvent(Event):
    """Specialized event for agent actions."""
    
    event_type: Literal[EventType.ACTION] = Field(default=EventType.ACTION)
    target: Optional[str] = Field(
        default=None,
        description="Target of the action (agent ID, object ID, etc.)"
    )
    success: bool = Field(default=True, description="Whether the action succeeded")


class DialogueEvent(Event):
    """Specialized event for dialogue between agents."""
    
    event_type: Literal[EventType.DIALOGUE] = Field(default=EventType.DIALOGUE)
    speaker_id: str = Field(..., description="ID of the speaking agent")
    listener_ids: List[str] = Field(
        default_factory=list,
        description="IDs of agents who heard the dialogue"
    )
    dialogue_text: str = Field(..., description="What was said")


class MovementEvent(Event):
    """Specialized event for agent movement."""
    
    event_type: Literal[EventType.MOVEMENT] = Field(default=EventType.MOVEMENT)
    from_location: Optional[str] = Field(
        default=None,
        description="Previous location"
    )
    to_location: str = Field(..., description="New location")


class EventQuery(BaseModel):
    """Query parameters for event search."""
    
    event_types: Optional[List[EventType]] = Field(
        default=None,
        description="Filter by event types"
    )
    agent_id: Optional[str] = Field(
        default=None,
        description="Filter by agent ID"
    )
    location: Optional[str] = Field(
        default=None,
        description="Filter by location"
    )
    start_time: Optional[datetime] = Field(
        default=None,
        description="Start of time range"
    )
    end_time: Optional[datetime] = Field(
        default=None,
        description="End of time range"
    )
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
