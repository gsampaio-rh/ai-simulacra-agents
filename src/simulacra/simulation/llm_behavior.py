"""LLM-powered behavior system for agents with real cognitive reasoning."""

import logging
import re
from typing import Dict, List, Optional, Tuple

from ..agents.memory_manager import MemoryManager
from ..llm.llm_service import LLMService
from ..models.action import Action, ActionType, MoveAction, WaitAction, ObserveAction, InteractAction
from ..models.agent import Agent
from .world_manager import WorldManager

logger = logging.getLogger(__name__)


class LLMBehavior:
    """LLM-powered behavior system that uses real AI reasoning for agent decisions."""
    
    def __init__(
        self, 
        world_manager: WorldManager, 
        llm_service: Optional[LLMService] = None,
        memory_manager: Optional[MemoryManager] = None
    ):
        """Initialize LLM behavior system.
        
        Args:
            world_manager: World state manager
            llm_service: LLM service for generating decisions (will create if None)
            memory_manager: Memory manager for retrieving relevant memories (optional)
        """
        self.world_manager = world_manager
        self.llm_service = llm_service or LLMService()
        self.memory_manager = memory_manager
    
    async def choose_action_with_reasoning(self, agent: Agent) -> Tuple[Action, str]:
        """Choose an action for an agent using LLM reasoning.
        
        Args:
            agent: The agent to choose an action for
            
        Returns:
            Tuple of (Action, reasoning_text)
        """
        try:
            # Get current context
            context = await self._build_agent_context(agent)
            
            # Generate LLM decision with reasoning
            action, reasoning = await self._generate_llm_decision(agent, context)
            
            logger.debug(f"LLM decision for {agent.name}: {action.action_type} - {reasoning}")
            return action, reasoning
            
        except Exception as e:
            logger.error(f"LLM decision failed for {agent.name}: {e}")
            # Fallback to a safe default action
            fallback_action = ObserveAction().to_action(agent.id)
            fallback_reasoning = f"Fallback to observation due to decision error: {str(e)}"
            return fallback_action, fallback_reasoning
    
    async def choose_action(self, agent: Agent) -> Action:
        """Choose an action for an agent (compatibility with existing system).
        
        Args:
            agent: The agent to choose an action for
            
        Returns:
            Action for the agent to perform
        """
        action, _ = await self.choose_action_with_reasoning(agent)
        return action
    
    async def _build_agent_context(self, agent: Agent) -> Dict:
        """Build contextual information for the agent's decision.
        
        Args:
            agent: The agent
            
        Returns:
            Context dictionary with current situation and memories
        """
        current_location = self.world_manager.get_agent_location(agent.id)
        
        if not current_location:
            # Agent not placed in world yet, place them at their home
            await self.world_manager.place_agent(agent.id, agent.home_location)
            current_location = agent.home_location
        
        # Get place information
        place_info = self.world_manager.get_place_info(current_location)
        place_name = place_info["name"] if place_info else current_location
        place_description = place_info.get("description", "") if place_info else ""
        
        # Get other agents at location
        other_agents = []
        if place_info:
            other_agents = [agent_id for agent_id in place_info.get("agents", []) if agent_id != agent.id]
        
        # Get connected places
        connected_places = self.world_manager.get_connected_places(current_location)
        available_destinations = []
        for place_id in connected_places:
            dest_info = self.world_manager.get_place_info(place_id)
            dest_name = dest_info["name"] if dest_info else place_id
            available_destinations.append(dest_name)
        
        # Retrieve relevant memories if memory manager is available
        relevant_memories = []
        if self.memory_manager:
            try:
                # Build context string for memory retrieval
                memory_context = f"Currently at {place_name}. "
                if other_agents:
                    memory_context += f"Other people here: {', '.join(other_agents)}. "
                if agent.state.current_task:
                    memory_context += f"Current task: {agent.state.current_task}. "
                memory_context += f"Energy: {agent.state.energy}%, Mood: {agent.state.mood}/10"
                
                # Retrieve relevant memories
                memory_results = await self.memory_manager.retrieve_relevant_memories(
                    agent.id, 
                    memory_context, 
                    limit=3
                )
                relevant_memories = [result.memory for result in memory_results]
                
            except Exception as e:
                logger.warning(f"Failed to retrieve memories for {agent.name}: {e}")
        
        return {
            "current_location": current_location,
            "place_name": place_name,
            "place_description": place_description,
            "other_agents": other_agents,
            "available_destinations": available_destinations,
            "agent_energy": agent.state.energy,
            "agent_mood": agent.state.mood,
            "current_task": agent.state.current_task,
            "relevant_memories": relevant_memories
        }
    
    async def _generate_llm_decision(self, agent: Agent, context: Dict) -> Tuple[Action, str]:
        """Generate action decision and reasoning using LLM.
        
        Args:
            agent: The agent making the decision
            context: Current context information
            
        Returns:
            Tuple of (Action, reasoning_text)
        """
        # Build the decision prompt
        prompt = self._build_decision_prompt(agent, context)
        
        logger.info(f"🎭 COGNITIVE PROCESS: {agent.name} is thinking and making decisions (location: {context.get('location', 'unknown')})")
        
        try:
            # Generate LLM response
            response = await self.llm_service.ollama_client.generate(
                model=self.llm_service.settings.ollama_model,
                prompt=prompt,
                options={
                    "temperature": 0.7,  # Allow for creative but consistent thinking
                    "top_p": 0.9,
                    "num_predict": 300
                }
            )
            
            # Parse the response
            action, reasoning = self._parse_llm_response(response.response, agent, context)
            
            logger.info(f"🎯 DECISION COMPLETE: {agent.name} chose '{action.action_type}' action")
            return action, reasoning
            
        except Exception as e:
            logger.error(f"LLM generation failed for {agent.name}: {e}")
            # Create a safe fallback
            fallback_action = ObserveAction().to_action(agent.id)
            fallback_reasoning = f"Using fallback observation due to LLM error"
            return fallback_action, fallback_reasoning
    
    def _build_decision_prompt(self, agent: Agent, context: Dict) -> str:
        """Build the prompt for LLM decision making.
        
        Args:
            agent: The agent
            context: Current context
            
        Returns:
            Formatted prompt string
        """
        # Build location context
        location_context = f"You are currently at {context['place_name']}"
        if context['place_description']:
            location_context += f" - {context['place_description']}"
        
        # Build social context
        social_context = ""
        if context['other_agents']:
            agents_list = ", ".join(context['other_agents'])
            social_context = f"Other people here: {agents_list}"
        else:
            social_context = "You are alone here"
        
        # Build destination options
        destinations_context = ""
        if context['available_destinations']:
            dest_list = ", ".join(context['available_destinations'])
            destinations_context = f"You can move to: {dest_list}"
        else:
            destinations_context = "No other places are directly accessible from here"
        
        # Build energy/mood context
        energy_context = f"Energy: {context['agent_energy']:.0f}% | Mood: {context['agent_mood']:.1f}/10"
        
        # Build task context
        task_context = ""
        if context['current_task']:
            task_context = f"Current task: {context['current_task']}"
        else:
            task_context = "No specific task at the moment"
        
        # Build memory context
        memory_context = ""
        if context['relevant_memories']:
            memory_context = "Recent relevant memories:\n"
            for i, memory in enumerate(context['relevant_memories'], 1):
                memory_context += f"  {i}. {memory.content}\n"
            memory_context += "\nConsider these experiences when deciding what to do next."
        
        prompt = f"""You are {agent.name}, a character in a social simulation.

Your background: {agent.bio}

Your personality: {agent.personality}

Current situation:
- {location_context}
- {social_context}
- {destinations_context}
- {energy_context}
- {task_context}

{memory_context}

What would you like to do next? Think about what this character would naturally want to do given their personality, current situation, social context, and past experiences.

Available actions:
1. MOVE to another location (specify which one from the available destinations)
2. WAIT and rest (specify why you're waiting)
3. OBSERVE your surroundings (look around and take in the environment)
4. INTERACT with the environment or people around you

Please respond in this exact format:

REASONING: [Your thoughts as {agent.name} - what are you thinking and feeling? Why do you want to take this action? Be authentic to your personality and situation. Consider how your past experiences influence this decision]

ACTION: [Choose exactly one: MOVE to [destination] | WAIT [reason] | OBSERVE | INTERACT [with what/whom]]

Remember: You are {agent.name}, with the personality traits "{agent.personality}". Think and act in character based on your experiences!"""

        return prompt
    
    def _parse_llm_response(self, response: str, agent: Agent, context: Dict) -> Tuple[Action, str]:
        """Parse LLM response into action and reasoning.
        
        Args:
            response: Raw LLM response
            agent: The agent
            context: Current context
            
        Returns:
            Tuple of (Action, reasoning_text)
        """
        try:
            # Extract reasoning
            reasoning_match = re.search(r'REASONING:\s*(.*?)(?=ACTION:|$)', response, re.DOTALL | re.IGNORECASE)
            reasoning = reasoning_match.group(1).strip() if reasoning_match else "I'm thinking about what to do next."
            
            # Extract action
            action_match = re.search(r'ACTION:\s*(.*?)(?:\n|$)', response, re.IGNORECASE)
            action_text = action_match.group(1).strip() if action_match else ""
            
            # Parse action into concrete Action object
            action = self._parse_action_text(action_text, agent, context)
            
            return action, reasoning
            
        except Exception as e:
            logger.warning(f"Failed to parse LLM response for {agent.name}: {e}")
            # Return safe fallback
            fallback_action = ObserveAction().to_action(agent.id)
            fallback_reasoning = "I need to observe my surroundings and think about my next move."
            return fallback_action, fallback_reasoning
    
    def _parse_action_text(self, action_text: str, agent: Agent, context: Dict) -> Action:
        """Parse action text into a concrete Action object.
        
        Args:
            action_text: The action text from LLM
            agent: The agent
            context: Current context
            
        Returns:
            Parsed Action object
        """
        action_text = action_text.strip().upper()
        
        if action_text.startswith("MOVE"):
            # Parse destination
            move_match = re.search(r'MOVE\s+(?:TO\s+)?(.*)', action_text)
            if move_match:
                destination_name = move_match.group(1).strip()
                
                # Find matching place ID
                for place_id in context['available_destinations']:
                    place_info = self.world_manager.get_place_info(place_id)
                    if place_info and destination_name.lower() in place_info["name"].lower():
                        return MoveAction(target_place_id=place_id).to_action(agent.id)
                
                # If no exact match, try the first available destination
                connected_places = self.world_manager.get_connected_places(context['current_location'])
                if connected_places:
                    return MoveAction(target_place_id=connected_places[0]).to_action(agent.id)
        
        elif action_text.startswith("WAIT"):
            # Parse wait reason
            wait_match = re.search(r'WAIT\s*(.*)', action_text)
            reason = wait_match.group(1).strip() if wait_match else "resting and thinking"
            return WaitAction(duration_minutes=5, reason=reason).to_action(agent.id)
        
        elif action_text.startswith("OBSERVE"):
            return ObserveAction().to_action(agent.id)
        
        elif action_text.startswith("INTERACT"):
            # Parse interaction target
            interact_match = re.search(r'INTERACT\s*(.*)', action_text)
            target = interact_match.group(1).strip() if interact_match else "environment"
            return InteractAction(interaction_type=f"interact with {target}").to_action(agent.id)
        
        # Default fallback
        return ObserveAction().to_action(agent.id)
    
    async def health_check(self) -> bool:
        """Check if the LLM behavior system is working.
        
        Returns:
            True if system is healthy, False otherwise
        """
        try:
            return await self.llm_service.health_check()
        except Exception as e:
            logger.warning(f"LLM behavior health check failed: {e}")
            return False
