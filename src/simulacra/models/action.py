"""Action-related data models."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ActionType(Enum):
    """Types of actions that agents can perform."""
    
    MOVE = "move"
    WAIT = "wait"
    INTERACT = "interact"
    OBSERVE = "observe"


class Action(BaseModel):
    """An action that an agent can perform."""
    
    id: UUID = Field(default_factory=uuid4)
    agent_id: str = Field(..., description="ID of the agent performing the action")
    action_type: ActionType = Field(..., description="Type of action")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Action-specific parameters"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this action was created"
    )
    duration_minutes: int = Field(
        default=1,
        ge=1,
        description="How long this action takes"
    )
    success: Optional[bool] = Field(
        default=None,
        description="Whether the action succeeded (None if not executed yet)"
    )
    result_message: Optional[str] = Field(
        default=None,
        description="Description of action result"
    )
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class MoveAction(BaseModel):
    """Parameters for a move action."""
    
    target_place_id: str = Field(..., description="Place ID to move to")
    
    def to_action(self, agent_id: str) -> Action:
        """Convert to a generic Action."""
        return Action(
            agent_id=agent_id,
            action_type=ActionType.MOVE,
            parameters={"target_place_id": self.target_place_id},
            duration_minutes=1
        )


class WaitAction(BaseModel):
    """Parameters for a wait action."""
    
    duration_minutes: int = Field(default=5, ge=1, description="How long to wait")
    reason: Optional[str] = Field(default=None, description="Why the agent is waiting")
    
    def to_action(self, agent_id: str) -> Action:
        """Convert to a generic Action."""
        return Action(
            agent_id=agent_id,
            action_type=ActionType.WAIT,
            parameters={
                "duration_minutes": self.duration_minutes,
                "reason": self.reason
            },
            duration_minutes=self.duration_minutes
        )


class InteractAction(BaseModel):
    """Parameters for an interact action."""
    
    target_object_id: Optional[str] = Field(
        default=None,
        description="Object ID to interact with"
    )
    target_agent_id: Optional[str] = Field(
        default=None,
        description="Agent ID to interact with"
    )
    interaction_type: str = Field(..., description="Type of interaction")
    
    def to_action(self, agent_id: str) -> Action:
        """Convert to a generic Action."""
        return Action(
            agent_id=agent_id,
            action_type=ActionType.INTERACT,
            parameters={
                "target_object_id": self.target_object_id,
                "target_agent_id": self.target_agent_id,
                "interaction_type": self.interaction_type
            },
            duration_minutes=2
        )


class ObserveAction(BaseModel):
    """Parameters for an observe action."""
    
    target: Optional[str] = Field(
        default=None,
        description="What to observe (place, agent, object)"
    )
    
    def to_action(self, agent_id: str) -> Action:
        """Convert to a generic Action."""
        return Action(
            agent_id=agent_id,
            action_type=ActionType.OBSERVE,
            parameters={"target": self.target},
            duration_minutes=1
        )


class ActionResult(BaseModel):
    """Result of executing an action."""
    
    action_id: UUID = Field(..., description="ID of the executed action")
    success: bool = Field(..., description="Whether the action succeeded")
    message: str = Field(..., description="Description of what happened")
    side_effects: Dict[str, Any] = Field(
        default_factory=dict,
        description="Any side effects or state changes"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the action was executed"
    )
