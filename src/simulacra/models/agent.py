"""Agent-related data models."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AgentStatus(Enum):
    """Current status of an agent."""
    
    ACTIVE = "active"               # Agent is actively participating
    IDLE = "idle"                   # Agent is waiting/resting  
    REFLECTING = "reflecting"       # Agent is generating reflections
    PLANNING = "planning"           # Agent is updating plans
    OFFLINE = "offline"             # Agent is not participating


class AgentState(BaseModel):
    """Current state of an agent."""
    
    agent_id: str = Field(..., description="ID of the agent")
    status: AgentStatus = Field(default=AgentStatus.ACTIVE)
    current_location: Optional[str] = Field(
        default=None,
        description="Current place ID"
    )
    current_task: Optional[str] = Field(
        default=None,
        description="Description of current task"
    )
    energy: float = Field(
        default=100.0,
        ge=0.0,
        le=100.0,
        description="Energy level (0-100)"
    )
    mood: float = Field(
        default=5.0,
        ge=0.0,
        le=10.0,
        description="Mood level (0-10)"
    )
    last_reflection_time: Optional[datetime] = Field(
        default=None,
        description="When the agent last reflected"
    )
    importance_accumulator: float = Field(
        default=0.0,
        ge=0.0,
        description="Accumulated importance since last reflection"
    )
    last_updated: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this state was last updated"
    )
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class Agent(BaseModel):
    """An autonomous agent in the simulation."""
    
    id: str = Field(..., description="Unique identifier for the agent")
    name: str = Field(..., description="Human-readable name")
    bio: str = Field(..., description="Background and description")
    personality: str = Field(..., description="Personality traits and characteristics")
    home_location: str = Field(..., description="Agent's home place ID")
    relationships: Dict[str, str] = Field(
        default_factory=dict,
        description="Relationships with other agents (agent_id -> relationship_type)"
    )
    memories_count: int = Field(
        default=0,
        ge=0,
        description="Total number of memories"
    )
    reflections_count: int = Field(
        default=0,
        ge=0,
        description="Total number of reflections"
    )
    state: AgentState = Field(
        default_factory=lambda: AgentState(agent_id=""),
        description="Current agent state"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this agent was created"
    )
    
    def __init__(self, **data):
        """Initialize agent with proper state setup."""
        super().__init__(**data)
        # Ensure state has correct agent_id
        if self.state.agent_id != self.id:
            self.state.agent_id = self.id
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class AgentConfiguration(BaseModel):
    """Configuration for creating an agent."""
    
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Agent name")
    bio: str = Field(..., description="Agent background")
    personality: str = Field(..., description="Personality description")
    home_location: str = Field(..., description="Home place ID")
    relationships: Dict[str, str] = Field(
        default_factory=dict,
        description="Initial relationships"
    )
    
    def to_agent(self) -> Agent:
        """Convert configuration to an Agent."""
        return Agent(
            id=self.id,
            name=self.name,
            bio=self.bio,
            personality=self.personality,
            home_location=self.home_location,
            relationships=self.relationships,
            state=AgentState(agent_id=self.id)
        )


class AgentQuery(BaseModel):
    """Query parameters for agent search."""
    
    agent_ids: Optional[List[str]] = Field(
        default=None,
        description="Specific agent IDs to retrieve"
    )
    status: Optional[AgentStatus] = Field(
        default=None,
        description="Filter by agent status"
    )
    location: Optional[str] = Field(
        default=None,
        description="Filter by current location"
    )
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class AgentSummary(BaseModel):
    """Summary information about an agent."""
    
    id: str
    name: str
    status: AgentStatus
    current_location: Optional[str]
    current_task: Optional[str]
    energy: float
    memories_count: int
    reflections_count: int
    last_updated: datetime
    
    @classmethod
    def from_agent(cls, agent: Agent) -> "AgentSummary":
        """Create summary from full agent."""
        return cls(
            id=agent.id,
            name=agent.name,
            status=agent.state.status,
            current_location=agent.state.current_location,
            current_task=agent.state.current_task,
            energy=agent.state.energy,
            memories_count=agent.memories_count,
            reflections_count=agent.reflections_count,
            last_updated=agent.state.last_updated
        )
