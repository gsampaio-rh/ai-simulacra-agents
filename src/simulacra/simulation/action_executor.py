"""Action execution engine for agent actions."""

import logging
import random
from typing import List, Optional

from ..models.action import Action, ActionType, ActionResult
from ..models.event import Event, EventType
from .world_manager import WorldManager

logger = logging.getLogger(__name__)


class ActionExecutor:
    """Executes agent actions and generates events."""
    
    def __init__(self, world_manager: WorldManager):
        """Initialize action executor.
        
        Args:
            world_manager: World state manager
        """
        self.world_manager = world_manager
    
    async def execute_action(self, action: Action) -> ActionResult:
        """Execute an agent action.
        
        Args:
            action: The action to execute
            
        Returns:
            Result of the action execution
        """
        logger.debug(f"Executing action {action.action_type.value if hasattr(action.action_type, 'value') else str(action.action_type)} for agent {action.agent_id}")
        
        try:
            # Handle both enum and string action types
            action_type_str = action.action_type.value if hasattr(action.action_type, 'value') else str(action.action_type)
            
            if action_type_str == "move":
                return await self._execute_move(action)
            elif action_type_str == "wait":
                return await self._execute_wait(action)
            elif action_type_str == "interact":
                return await self._execute_interact(action)
            elif action_type_str == "observe":
                return await self._execute_observe(action)
            else:
                return ActionResult(
                    action_id=action.id,
                    success=False,
                    message=f"Unknown action type: {action_type_str}"
                )
        
        except Exception as e:
            logger.error(f"Error executing action {action.id}: {e}")
            return ActionResult(
                action_id=action.id,
                success=False,
                message=f"Action failed with error: {str(e)}"
            )
    
    async def _execute_move(self, action: Action) -> ActionResult:
        """Execute a move action."""
        target_place_id = action.parameters.get("target_place_id")
        if not target_place_id:
            return ActionResult(
                action_id=action.id,
                success=False,
                message="Move action missing target_place_id parameter"
            )
        
        # Get current location
        current_location = self.world_manager.get_agent_location(action.agent_id)
        
        # Attempt to move
        success = await self.world_manager.move_agent(action.agent_id, target_place_id)
        
        if success:
            # Get place info for result message
            place_info = self.world_manager.get_place_info(target_place_id)
            place_name = place_info["name"] if place_info else target_place_id
            
            return ActionResult(
                action_id=action.id,
                success=True,
                message=f"Moved from {current_location} to {place_name}",
                side_effects={
                    "previous_location": current_location,
                    "new_location": target_place_id
                }
            )
        else:
            return ActionResult(
                action_id=action.id,
                success=False,
                message=f"Cannot move from {current_location} to {target_place_id} - not connected or place doesn't exist"
            )
    
    async def _execute_wait(self, action: Action) -> ActionResult:
        """Execute a wait action."""
        duration = action.parameters.get("duration_minutes", 5)
        reason = action.parameters.get("reason", "")
        
        current_location = self.world_manager.get_agent_location(action.agent_id)
        
        message = f"Waited for {duration} minutes"
        if reason:
            message += f" ({reason})"
        if current_location:
            place_info = self.world_manager.get_place_info(current_location)
            place_name = place_info["name"] if place_info else current_location
            message += f" at {place_name}"
        
        return ActionResult(
            action_id=action.id,
            success=True,
            message=message,
            side_effects={"duration_minutes": duration}
        )
    
    async def _execute_interact(self, action: Action) -> ActionResult:
        """Execute an interact action."""
        target_object_id = action.parameters.get("target_object_id")
        target_agent_id = action.parameters.get("target_agent_id")
        interaction_type = action.parameters.get("interaction_type", "generic")
        
        current_location = self.world_manager.get_agent_location(action.agent_id)
        
        if target_object_id:
            # Interacting with an object
            return ActionResult(
                action_id=action.id,
                success=True,
                message=f"Performed {interaction_type} interaction with {target_object_id}",
                side_effects={
                    "target_object": target_object_id,
                    "interaction_type": interaction_type,
                    "location": current_location
                }
            )
        
        elif target_agent_id:
            # Interacting with another agent
            target_location = self.world_manager.get_agent_location(target_agent_id)
            
            if target_location != current_location:
                return ActionResult(
                    action_id=action.id,
                    success=False,
                    message=f"Cannot interact with {target_agent_id} - they are not in the same location"
                )
            
            return ActionResult(
                action_id=action.id,
                success=True,
                message=f"Performed {interaction_type} interaction with {target_agent_id}",
                side_effects={
                    "target_agent": target_agent_id,
                    "interaction_type": interaction_type,
                    "location": current_location
                }
            )
        
        else:
            # Generic interaction with environment
            return ActionResult(
                action_id=action.id,
                success=True,
                message=f"Performed {interaction_type} interaction with the environment",
                side_effects={
                    "interaction_type": interaction_type,
                    "location": current_location
                }
            )
    
    async def _execute_observe(self, action: Action) -> ActionResult:
        """Execute an observe action."""
        target = action.parameters.get("target")
        current_location = self.world_manager.get_agent_location(action.agent_id)
        
        if not current_location:
            return ActionResult(
                action_id=action.id,
                success=False,
                message="Cannot observe - agent location unknown"
            )
        
        # Get information about current location
        place_info = self.world_manager.get_place_info(current_location)
        if not place_info:
            return ActionResult(
                action_id=action.id,
                success=False,
                message=f"Cannot observe - unknown location {current_location}"
            )
        
        # Generate observation based on what's at the location
        observations = []
        
        # Observe the place itself
        observations.append(f"At {place_info['name']}: {place_info.get('description', 'A place in the simulation')}")
        
        # Observe other agents
        other_agents = [agent for agent in place_info['agents'] if agent != action.agent_id]
        if other_agents:
            agent_list = ", ".join(other_agents)
            observations.append(f"Other agents here: {agent_list}")
        else:
            observations.append("No other agents here")
        
        # TODO: Observe objects when we implement object system more fully
        
        observation_text = ". ".join(observations)
        
        return ActionResult(
            action_id=action.id,
            success=True,
            message=f"Observed surroundings: {observation_text}",
            side_effects={
                "location": current_location,
                "place_info": place_info,
                "other_agents": other_agents
            }
        )
    
    def get_available_actions(self, agent_id: str) -> List[str]:
        """Get list of available actions for an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            List of available action descriptions
        """
        actions = []
        
        current_location = self.world_manager.get_agent_location(agent_id)
        if current_location:
            # Get connected places for movement
            connected_places = self.world_manager.get_connected_places(current_location)
            for place_id in connected_places:
                place_info = self.world_manager.get_place_info(place_id)
                place_name = place_info["name"] if place_info else place_id
                actions.append(f"move to {place_name}")
        
        # Basic actions always available
        actions.extend([
            "wait and rest",
            "observe surroundings",
            "interact with environment"
        ])
        
        # TODO: Add interactions with specific objects and agents
        
        return actions
