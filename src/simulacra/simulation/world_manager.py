"""World state management for simulation."""

import logging
from typing import Dict, List, Optional

from ..config.world_config import WorldConfigLoader
from ..models.world import WorldState, AgentLocation
from ..storage.sqlite_store import SQLiteStore

logger = logging.getLogger(__name__)


class WorldManager:
    """Manages the current state of the simulation world."""
    
    def __init__(self, config_loader: WorldConfigLoader, storage: SQLiteStore):
        """Initialize world manager.
        
        Args:
            config_loader: Loader for world configuration
            storage: Storage for persistence
        """
        self.config_loader = config_loader
        self.storage = storage
        self._world_state: Optional[WorldState] = None
    
    async def initialize(self) -> None:
        """Initialize world state from configuration."""
        # Load world configuration
        world_config = self.config_loader.load_world_config()
        
        # Create initial world state
        self._world_state = world_config.to_world_state()
        
        # Store places and objects in database
        await self.storage.connect()
        
        # Create places
        for place in world_config.places:
            try:
                await self.storage.create_place(place)
                logger.debug(f"Created place: {place.name} ({place.id})")
            except Exception as e:
                # Place might already exist, that's okay
                logger.debug(f"Place {place.id} already exists: {e}")
        
        # Create objects
        for obj in world_config.objects:
            try:
                await self.storage.create_object(obj)
                logger.debug(f"Created object: {obj.name} ({obj.id})")
            except Exception as e:
                # Object might already exist, that's okay
                logger.debug(f"Object {obj.id} already exists: {e}")
        
        logger.info(f"World initialized with {len(self._world_state.places)} places and {len(self._world_state.objects)} objects")
    
    @property
    def world_state(self) -> WorldState:
        """Get current world state."""
        if self._world_state is None:
            raise RuntimeError("World not initialized. Call initialize() first.")
        return self._world_state
    
    async def place_agent(self, agent_id: str, place_id: str) -> bool:
        """Place an agent at a specific location.
        
        Args:
            agent_id: ID of the agent to place
            place_id: ID of the place to place them at
            
        Returns:
            True if successful, False otherwise
        """
        if place_id not in self.world_state.places:
            logger.warning(f"Cannot place agent {agent_id} at unknown place {place_id}")
            return False
        
        # Create agent location
        agent_location = AgentLocation(
            agent_id=agent_id,
            place_id=place_id
        )
        
        # Update world state
        self.world_state.agent_locations[agent_id] = agent_location
        
        # Update storage
        await self.storage.update_agent_location(agent_location)
        
        logger.debug(f"Placed agent {agent_id} at {place_id}")
        return True
    
    async def move_agent(self, agent_id: str, target_place_id: str) -> bool:
        """Move an agent to a new location.
        
        Args:
            agent_id: ID of the agent to move
            target_place_id: ID of the target place
            
        Returns:
            True if move was successful, False otherwise
        """
        # Check if move is valid
        if not self.world_state.can_move_to(agent_id, target_place_id):
            current_loc = self.world_state.agent_locations.get(agent_id)
            current_place = current_loc.place_id if current_loc else "unknown"
            logger.debug(f"Cannot move agent {agent_id} from {current_place} to {target_place_id}")
            return False
        
        # Perform the move
        if self.world_state.move_agent(agent_id, target_place_id):
            # Update storage
            agent_location = self.world_state.agent_locations[agent_id]
            await self.storage.update_agent_location(agent_location)
            
            logger.debug(f"Moved agent {agent_id} to {target_place_id}")
            return True
        
        return False
    
    def get_agent_location(self, agent_id: str) -> Optional[str]:
        """Get current location of an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Place ID where agent is located, or None if not found
        """
        agent_location = self.world_state.agent_locations.get(agent_id)
        return agent_location.place_id if agent_location else None
    
    def get_agents_at_location(self, place_id: str) -> List[str]:
        """Get all agents at a specific location.
        
        Args:
            place_id: ID of the place
            
        Returns:
            List of agent IDs at the location
        """
        return self.world_state.get_agents_at_location(place_id)
    
    def get_connected_places(self, place_id: str) -> List[str]:
        """Get places connected to a given place.
        
        Args:
            place_id: ID of the place
            
        Returns:
            List of connected place IDs
        """
        place = self.world_state.places.get(place_id)
        return place.connected_places if place else []
    
    def get_place_info(self, place_id: str) -> Optional[Dict]:
        """Get information about a place.
        
        Args:
            place_id: ID of the place
            
        Returns:
            Dictionary with place information, or None if not found
        """
        place = self.world_state.places.get(place_id)
        if not place:
            return None
        
        agents_here = self.get_agents_at_location(place_id)
        
        return {
            "id": place.id,
            "name": place.name,
            "description": place.description,
            "capacity": place.capacity,
            "current_occupancy": len(agents_here),
            "agents": agents_here,
            "connected_places": place.connected_places,
            "properties": place.properties
        }
    
    def get_world_summary(self) -> Dict:
        """Get a summary of the current world state.
        
        Returns:
            Dictionary with world state summary
        """
        total_agents = len(self.world_state.agent_locations)
        place_occupancy = {}
        
        for place_id in self.world_state.places:
            agents_here = self.get_agents_at_location(place_id)
            place_occupancy[place_id] = {
                "name": self.world_state.places[place_id].name,
                "agent_count": len(agents_here),
                "agents": agents_here
            }
        
        return {
            "total_places": len(self.world_state.places),
            "total_objects": len(self.world_state.objects),
            "total_agents": total_agents,
            "place_occupancy": place_occupancy,
            "last_updated": self.world_state.last_updated.isoformat()
        }
