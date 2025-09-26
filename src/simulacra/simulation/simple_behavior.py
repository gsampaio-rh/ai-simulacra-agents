"""Simple behavior system for agents without memory."""

import logging
import random
from typing import List, Optional

from ..models.action import Action, MoveAction, WaitAction, ObserveAction
from ..models.agent import Agent
from .world_manager import WorldManager

logger = logging.getLogger(__name__)


class SimpleBehavior:
    """Simple behavior system for basic agent actions."""
    
    def __init__(self, world_manager: WorldManager):
        """Initialize simple behavior system.
        
        Args:
            world_manager: World state manager
        """
        self.world_manager = world_manager
        self.agent_last_actions: dict[str, str] = {}  # Track last action to avoid loops
    
    async def choose_action(self, agent: Agent) -> Action:
        """Choose an action for an agent based on simple rules.
        
        Args:
            agent: The agent to choose an action for
            
        Returns:
            Action for the agent to perform
        """
        current_location = self.world_manager.get_agent_location(agent.id)
        
        if not current_location:
            # Agent not placed in world yet, place them at their home
            await self.world_manager.place_agent(agent.id, agent.home_location)
            current_location = agent.home_location
            
            return ObserveAction().to_action(agent.id)
        
        # Get possible moves
        connected_places = self.world_manager.get_connected_places(current_location)
        last_action = self.agent_last_actions.get(agent.id, "")
        
        # Simple personality-based behavior
        action = self._choose_personality_based_action(agent, current_location, connected_places, last_action)
        
        # Remember this action
        self.agent_last_actions[agent.id] = action.action_type.value if hasattr(action.action_type, 'value') else str(action.action_type)
        
        return action
    
    def _choose_personality_based_action(
        self, 
        agent: Agent, 
        current_location: str, 
        connected_places: List[str],
        last_action: str
    ) -> Action:
        """Choose action based on agent personality.
        
        Args:
            agent: The agent
            current_location: Current place ID
            connected_places: Places agent can move to
            last_action: Last action type performed
            
        Returns:
            Chosen action
        """
        personality = agent.personality.lower()
        
        # Avoid doing the same action repeatedly
        if last_action == "wait" and random.random() < 0.7:
            # If we just waited, prefer to move or observe
            if connected_places and random.random() < 0.8:
                return self._choose_move_action(connected_places)
            else:
                return ObserveAction().to_action(agent.id)
        
        # Personality-based tendencies
        if "social" in personality or "community" in personality:
            # Social agents prefer to move to busier places
            return self._choose_social_action(agent, current_location, connected_places)
        
        elif "introverted" in personality or "quiet" in personality:
            # Introverted agents prefer quieter places and observation
            return self._choose_introverted_action(agent, current_location, connected_places)
        
        elif "active" in personality or "energetic" in personality:
            # Active agents prefer to move around
            if connected_places and random.random() < 0.7:
                return self._choose_move_action(connected_places)
            else:
                return ObserveAction().to_action(agent.id)
        
        else:
            # Default behavior - random choice
            return self._choose_random_action(current_location, connected_places)
    
    def _choose_social_action(self, agent: Agent, current_location: str, connected_places: List[str]) -> Action:
        """Choose action for social agents."""
        # Look for places with other agents
        best_place = None
        most_agents = -1
        
        for place_id in connected_places:
            agents_there = self.world_manager.get_agents_at_location(place_id)
            if len(agents_there) > most_agents:
                most_agents = len(agents_there)
                best_place = place_id
        
        # Move to busiest place if found, otherwise explore
        if best_place and most_agents > 0:
            return MoveAction(target_place_id=best_place).to_action(agent.id)
        elif connected_places and random.random() < 0.6:
            return self._choose_move_action(connected_places)
        else:
            # Wait and observe, might attract others
            return WaitAction(
                duration_minutes=random.randint(3, 8),
                reason="socializing and people-watching"
            ).to_action(agent.id)
    
    def _choose_introverted_action(self, agent: Agent, current_location: str, connected_places: List[str]) -> Action:
        """Choose action for introverted agents."""
        # Check if current location is crowded
        current_occupancy = len(self.world_manager.get_agents_at_location(current_location))
        
        if current_occupancy > 2:  # Too crowded, find a quieter place
            quietest_place = None
            fewest_agents = float('inf')
            
            for place_id in connected_places:
                agents_there = self.world_manager.get_agents_at_location(place_id)
                if len(agents_there) < fewest_agents:
                    fewest_agents = len(agents_there)
                    quietest_place = place_id
            
            if quietest_place:
                return MoveAction(target_place_id=quietest_place).to_action(agent.id)
        
        # Prefer to observe or wait quietly
        if random.random() < 0.6:
            return ObserveAction().to_action(agent.id)
        else:
            return WaitAction(
                duration_minutes=random.randint(5, 10),
                reason="enjoying the peaceful atmosphere"
            ).to_action(agent.id)
    
    def _choose_move_action(self, connected_places: List[str]) -> Action:
        """Choose a random move action."""
        target_place = random.choice(connected_places)
        return MoveAction(target_place_id=target_place).to_action("dummy")  # Agent ID will be set by caller
    
    def _choose_random_action(self, current_location: str, connected_places: List[str]) -> Action:
        """Choose a random action."""
        action_weights = [
            (0.4, "move"),
            (0.3, "wait"),
            (0.3, "observe")
        ]
        
        rand = random.random()
        cumulative = 0.0
        
        for weight, action_type in action_weights:
            cumulative += weight
            if rand < cumulative:
                if action_type == "move" and connected_places:
                    return self._choose_move_action(connected_places)
                elif action_type == "wait":
                    return WaitAction(
                        duration_minutes=random.randint(3, 7),
                        reason="thinking and relaxing"
                    ).to_action("dummy")
                else:
                    return ObserveAction().to_action("dummy")
        
        # Fallback
        return ObserveAction().to_action("dummy")
