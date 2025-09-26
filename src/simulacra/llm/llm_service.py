"""LLM service for text generation and reasoning."""

import logging
from typing import Dict, List, Optional

from ..config import Settings
from ..models.agent import Agent
from ..models.memory import Memory
from .ollama_client import OllamaClient, OllamaError

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM-powered text generation and reasoning."""
    
    def __init__(self, settings: Optional[Settings] = None):
        """Initialize LLM service.
        
        Args:
            settings: Application settings (will use defaults if None)
        """
        if settings is None:
            from ..config import get_settings
            settings = get_settings()
        
        self.settings = settings
        self.ollama_client = OllamaClient(
            base_url=settings.ollama_base_url,
            timeout=settings.ollama_timeout
        )
    
    async def generate_reflection(
        self,
        agent: Agent,
        memories: List[Memory],
        max_insights: int = 5
    ) -> List[str]:
        """Generate reflection insights from memories.
        
        Args:
            agent: The agent generating reflections
            memories: Recent memories to reflect on
            max_insights: Maximum number of insights to generate
            
        Returns:
            List of reflection insights
        """
        if not memories:
            return []
        
        # Build context about the agent
        agent_context = f"""Agent: {agent.name}
Bio: {agent.bio}
Personality: {agent.personality}
Current location: {agent.state.current_location or "unknown"}"""
        
        # Build memory context
        memory_context = "\n".join([
            f"- {memory.content} (importance: {memory.importance_score:.1f})"
            for memory in memories[-20:]  # Last 20 memories
        ])
        
        prompt = f"""{agent_context}

Recent memories:
{memory_context}

Based on these recent memories, generate {max_insights} high-level insights about what {agent.name} has been experiencing, learning, or feeling. Each insight should:
1. Synthesize information from multiple memories
2. Reveal patterns or themes in the agent's experience
3. Be something the agent would naturally think about
4. Be specific to this agent's personality and situation

Format your response as a numbered list:
1. [First insight]
2. [Second insight]
...

Focus on insights that would be meaningful for {agent.name}'s future decisions and behavior."""

        logger.info(f"🧠 COGNITIVE PROCESS: Generating reflection insights for {agent.name} (based on {len(memories)} memories)")
        
        try:
            async with self.ollama_client as client:
                response = await client.generate(
                    model=self.settings.ollama_model,
                    prompt=prompt,
                    options={
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 500
                    }
                )
                
                # Parse insights from response
                insights = self._parse_numbered_list(response.response, max_insights)
                
                logger.info(f"✨ REFLECTION COMPLETE: Generated {len(insights)} insights for {agent.name}")
                return insights
                
        except Exception as e:
            logger.error(f"Failed to generate reflection for {agent.name}: {e}")
            raise OllamaError(f"Reflection generation failed: {str(e)}")
    
    async def generate_daily_plan(
        self,
        agent: Agent,
        memories: List[Memory],
        current_time: str = "morning"
    ) -> Dict[str, str]:
        """Generate a daily plan for an agent.
        
        Args:
            agent: The agent to plan for
            memories: Recent memories for context
            current_time: Current time of day
            
        Returns:
            Dictionary with plan components
        """
        # Build context
        agent_context = f"""Agent: {agent.name}
Bio: {agent.bio}
Personality: {agent.personality}
Home: {agent.home_location}
Current location: {agent.state.current_location or agent.home_location}"""
        
        # Recent memory context (brief)
        memory_context = ""
        if memories:
            recent_memories = memories[-10:]  # Last 10 memories
            memory_context = "Recent experiences:\n" + "\n".join([
                f"- {memory.content}"
                for memory in recent_memories
            ])
        
        prompt = f"""{agent_context}

{memory_context}

It's {current_time}. Create a realistic daily plan for {agent.name} that fits their personality and situation.

Consider:
- Their personality traits: {agent.personality}
- Their usual activities and responsibilities
- Their relationships and social connections
- Any recent experiences that might influence their plans

Provide a plan with these components:
1. Overall goal for the day (one sentence)
2. Morning activities (2-3 activities)
3. Afternoon activities (2-3 activities) 
4. Evening activities (1-2 activities)

Keep activities realistic and specific to this character. Each activity should be something they could reasonably do in their environment."""

        try:
            async with self.ollama_client as client:
                response = await client.generate(
                    model=self.settings.ollama_model,
                    prompt=prompt,
                    options={
                        "temperature": 0.6,
                        "top_p": 0.9,
                        "num_predict": 400
                    }
                )
                
                # Parse plan components
                plan = self._parse_daily_plan(response.response)
                
                logger.debug(f"Generated daily plan for {agent.name}")
                return plan
                
        except Exception as e:
            logger.error(f"Failed to generate daily plan for {agent.name}: {e}")
            raise OllamaError(f"Daily plan generation failed: {str(e)}")
    
    async def generate_action_decision(
        self,
        agent: Agent,
        current_context: str,
        available_actions: List[str],
        memories: List[Memory]
    ) -> str:
        """Generate action decision for an agent.
        
        Args:
            agent: The agent making the decision
            current_context: Current situation description
            available_actions: List of possible actions
            memories: Relevant memories for context
            
        Returns:
            Chosen action
        """
        # Build context
        agent_context = f"""Agent: {agent.name} 
Personality: {agent.personality}
Current task: {agent.state.current_task or "none"}
Energy: {agent.state.energy:.1f}/100
Mood: {agent.state.mood:.1f}/10"""
        
        # Memory context
        memory_context = ""
        if memories:
            memory_context = "Relevant memories:\n" + "\n".join([
                f"- {memory.content}"
                for memory in memories[-5:]  # Last 5 relevant memories
            ])
        
        actions_text = "\n".join([f"- {action}" for action in available_actions])
        
        prompt = f"""{agent_context}

Current situation:
{current_context}

{memory_context}

Available actions:
{actions_text}

Based on {agent.name}'s personality, current state, and the situation, choose the most appropriate action. Consider:
- What would this character naturally do?
- How do their personality traits influence their choice?
- What are their current needs and goals?
- How do recent memories affect their decision?

Respond with only the chosen action from the list above, exactly as written."""

        try:
            async with self.ollama_client as client:
                response = await client.generate(
                    model=self.settings.ollama_model,
                    prompt=prompt,
                    options={
                        "temperature": 0.4,  # Lower temperature for more consistent decisions
                        "top_p": 0.8,
                        "num_predict": 50
                    }
                )
                
                # Find matching action
                chosen_action = response.response.strip()
                
                # Try to match with available actions
                for action in available_actions:
                    if action.lower() in chosen_action.lower() or chosen_action.lower() in action.lower():
                        return action
                
                # If no exact match, return first available action as fallback
                logger.warning(f"Could not match LLM response '{chosen_action}' to available actions")
                return available_actions[0] if available_actions else "wait"
                
        except Exception as e:
            logger.error(f"Failed to generate action decision for {agent.name}: {e}")
            # Fallback to first action
            return available_actions[0] if available_actions else "wait"
    
    def _parse_numbered_list(self, text: str, max_items: int) -> List[str]:
        """Parse numbered list from LLM response.
        
        Args:
            text: Raw LLM response
            max_items: Maximum items to extract
            
        Returns:
            List of parsed items
        """
        items = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for numbered items (1., 2., etc.)
            if line and any(line.startswith(f"{i}.") for i in range(1, max_items + 1)):
                # Remove number and clean up
                item = line.split('.', 1)[1].strip()
                if item:
                    items.append(item)
                    
            if len(items) >= max_items:
                break
        
        return items
    
    def _parse_daily_plan(self, text: str) -> Dict[str, str]:
        """Parse daily plan from LLM response.
        
        Args:
            text: Raw LLM response
            
        Returns:
            Dictionary with plan components
        """
        plan = {
            "goal": "",
            "morning": "",
            "afternoon": "",
            "evening": ""
        }
        
        lines = text.strip().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Identify sections
            line_lower = line.lower()
            if "goal" in line_lower and ("day" in line_lower or "overall" in line_lower):
                current_section = "goal"
                # Extract goal from same line if present
                if ":" in line:
                    plan["goal"] = line.split(":", 1)[1].strip()
            elif "morning" in line_lower:
                current_section = "morning"
            elif "afternoon" in line_lower:
                current_section = "afternoon"
            elif "evening" in line_lower:
                current_section = "evening"
            elif current_section and line:
                # Add content to current section
                if plan[current_section]:
                    plan[current_section] += " " + line
                else:
                    plan[current_section] = line
        
        # Clean up any numbering or bullet points
        for key in plan:
            plan[key] = plan[key].replace("1.", "").replace("2.", "").replace("3.", "").replace("-", "").strip()
        
        return plan
    
    async def health_check(self) -> bool:
        """Check if the LLM service is working.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            async with self.ollama_client as client:
                health = await client.health_check()
                if not health:
                    return False
                
                # Test text generation
                response = await client.generate(
                    model=self.settings.ollama_model,
                    prompt="Say 'healthy' if you can respond.",
                    options={"num_predict": 10}
                )
                
                return "healthy" in response.response.lower()
                
        except Exception as e:
            logger.warning(f"LLM service health check failed: {e}")
            return False
