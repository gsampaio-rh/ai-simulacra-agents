"""Planning-related data models."""

from datetime import datetime, time, timedelta
from datetime import date as Date
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ActionType(Enum):
    """Types of actions an agent can perform."""
    
    MOVE = "move"                   # Move to a different location
    SAY = "say"                     # Speak to other agents
    INTERACT = "interact"           # Interact with objects
    WAIT = "wait"                   # Wait/idle
    REFLECT = "reflect"             # Trigger reflection
    PLAN = "plan"                   # Update planning


class TaskStatus(Enum):
    """Status of a task in the plan."""
    
    PENDING = "pending"             # Not yet started
    IN_PROGRESS = "in_progress"     # Currently executing
    COMPLETED = "completed"         # Successfully finished
    CANCELLED = "cancelled"         # Cancelled before completion
    FAILED = "failed"              # Failed during execution


class Task(BaseModel):
    """A specific task within a plan."""
    
    id: UUID = Field(default_factory=uuid4)
    description: str = Field(..., description="What the agent should do")
    action_type: ActionType = Field(..., description="Type of action to perform")
    duration_minutes: int = Field(
        default=5, 
        ge=1, 
        le=480,  # Max 8 hours for longer tasks
        description="Expected duration in minutes"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Action-specific parameters"
    )
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    location: Optional[str] = Field(
        default=None,
        description="Where this task should be performed"
    )
    prerequisites: List[UUID] = Field(
        default_factory=list,
        description="Task IDs that must complete first"
    )
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class HourlyBlock(BaseModel):
    """A block of time within a daily plan."""
    
    id: UUID = Field(default_factory=uuid4)
    start_time: time = Field(..., description="Start time for this block")
    duration_minutes: int = Field(
        default=60,
        ge=5,
        le=720,  # Max 12 hours
        description="Duration in minutes"
    )
    activity: str = Field(..., description="High-level activity description")
    location: Optional[str] = Field(
        default=None,
        description="Primary location for this activity"
    )
    tasks: List[Task] = Field(
        default_factory=list,
        description="Specific tasks within this block"
    )
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    
    @property
    def end_time(self) -> time:
        """Calculate the end time of this block."""
        start_dt = datetime.combine(Date.today(), self.start_time)
        end_dt = start_dt + timedelta(minutes=self.duration_minutes)
        return end_dt.time()
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class DailyPlan(BaseModel):
    """A full day's plan for an agent."""
    
    id: UUID = Field(default_factory=uuid4)
    agent_id: str = Field(..., description="ID of the agent this plan belongs to")
    date: Date = Field(..., description="Date this plan is for")
    goals: List[str] = Field(
        default_factory=list,
        description="High-level goals for the day"
    )
    hourly_blocks: List[HourlyBlock] = Field(
        default_factory=list,
        description="Time blocks that make up the day"
    )
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class PlanQuery(BaseModel):
    """Query parameters for plan retrieval."""
    
    agent_id: Optional[str] = Field(default=None)
    start_date: Optional[Date] = Field(default=None)
    end_date: Optional[Date] = Field(default=None)
    status: Optional[TaskStatus] = Field(default=None)
    limit: int = Field(default=10, ge=1, le=100)


class PlanUpdate(BaseModel):
    """Request to update a plan."""
    
    plan_id: UUID = Field(..., description="ID of the plan to update")
    goals: Optional[List[str]] = Field(default=None)
    hourly_blocks: Optional[List[HourlyBlock]] = Field(default=None)
    status: Optional[TaskStatus] = Field(default=None)
