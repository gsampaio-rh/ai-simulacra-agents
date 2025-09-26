"""World-related data models."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Place(BaseModel):
    """A location in the simulation world."""
    
    id: str = Field(..., description="Unique identifier for the place")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Description of the place")
    capacity: int = Field(
        default=10, 
        ge=1,
        description="Maximum number of agents that can be here"
    )
    properties: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional place properties"
    )
    connected_places: List[str] = Field(
        default_factory=list,
        description="Place IDs that are directly accessible from here"
    )


class WorldObject(BaseModel):
    """An object in the simulation world."""
    
    id: str = Field(..., description="Unique identifier for the object")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Description of the object")
    location: str = Field(..., description="Place ID where this object is located")
    properties: Dict[str, Any] = Field(
        default_factory=dict,
        description="Object properties and state"
    )
    interactions: List[str] = Field(
        default_factory=list,
        description="Available interactions with this object"
    )
    is_movable: bool = Field(
        default=False,
        description="Whether this object can be moved"
    )


class AgentLocation(BaseModel):
    """Current location of an agent."""
    
    agent_id: str = Field(..., description="ID of the agent")
    place_id: str = Field(..., description="Current place ID")
    last_updated: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this location was last updated"
    )
    previous_place_id: Optional[str] = Field(
        default=None,
        description="Previous place ID for movement tracking"
    )


class WorldState(BaseModel):
    """Complete state of the simulation world."""
    
    places: Dict[str, Place] = Field(
        default_factory=dict,
        description="All places in the world"
    )
    objects: Dict[str, WorldObject] = Field(
        default_factory=dict,
        description="All objects in the world"
    )
    agent_locations: Dict[str, AgentLocation] = Field(
        default_factory=dict,
        description="Current locations of all agents"
    )
    last_updated: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this state was last updated"
    )
    
    def can_perceive(self, observer_id: str, event_location: str) -> bool:
        """Check if an agent can perceive an event at a location."""
        observer_location = self.agent_locations.get(observer_id)
        if not observer_location:
            return False
        return observer_location.place_id == event_location
    
    def get_agents_at_location(self, place_id: str) -> List[str]:
        """Get all agents currently at a specific location."""
        return [
            agent_id 
            for agent_id, location in self.agent_locations.items()
            if location.place_id == place_id
        ]
    
    def can_move_to(self, agent_id: str, target_place_id: str) -> bool:
        """Check if an agent can move to a target location."""
        current_location = self.agent_locations.get(agent_id)
        if not current_location:
            return False
        
        current_place = self.places.get(current_location.place_id)
        if not current_place:
            return False
        
        # Check if target place exists
        if target_place_id not in self.places:
            return False
        
        # Check if target place is directly accessible
        return target_place_id in current_place.connected_places
    
    def move_agent(self, agent_id: str, target_place_id: str) -> bool:
        """Move an agent to a new location."""
        if not self.can_move_to(agent_id, target_place_id):
            return False
        
        current_location = self.agent_locations.get(agent_id)
        if current_location:
            current_location.previous_place_id = current_location.place_id
            current_location.place_id = target_place_id
            current_location.last_updated = datetime.utcnow()
        else:
            # Agent not in world yet, add them
            self.agent_locations[agent_id] = AgentLocation(
                agent_id=agent_id,
                place_id=target_place_id
            )
        
        self.last_updated = datetime.utcnow()
        return True


class WorldConfiguration(BaseModel):
    """Configuration for initializing the world."""
    
    places: List[Place] = Field(default_factory=list)
    objects: List[WorldObject] = Field(default_factory=list)
    
    def to_world_state(self) -> WorldState:
        """Convert configuration to a WorldState."""
        return WorldState(
            places={place.id: place for place in self.places},
            objects={obj.id: obj for obj in self.objects}
        )
