"""Planning engine for generating and managing agent plans with LLM-powered goal-oriented behavior."""

import logging
import re
from datetime import datetime, date, time, timedelta
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

from ..config.settings import Settings
from ..llm.llm_service import LLMService
from ..models.agent import Agent
from ..models.memory import Memory
from ..models.planning import DailyPlan, HourlyBlock, Task, TaskStatus, ActionType
from ..storage.sqlite_store import SQLiteStore
from .memory_manager import MemoryManager

logger = logging.getLogger(__name__)


class PlanningEngine:
    """Generates and manages goal-oriented plans for agents using LLM reasoning."""
    
    def __init__(
        self,
        memory_manager: MemoryManager,
        sqlite_store: SQLiteStore,
        llm_service: LLMService,
        settings: Optional[Settings] = None
    ):
        """Initialize planning engine.
        
        Args:
            memory_manager: Memory manager for retrieving context
            sqlite_store: SQLite store for persisting plans
            llm_service: LLM service for plan generation
            settings: Application settings (will create if None)
        """
        self.memory_manager = memory_manager
        self.sqlite_store = sqlite_store
        self.llm_service = llm_service
        self.settings = settings or Settings()
    
    async def should_plan(self, agent: Agent) -> bool:
        """Check if an agent should generate or update their daily plan.
        
        Args:
            agent: The agent to check
            
        Returns:
            True if agent should plan, False otherwise
        """
        try:
            # Check if agent has a plan for today
            current_plan = await self.get_current_daily_plan(agent.id)
            
            if not current_plan:
                logger.info(f"🎯 {agent.name} has no plan for today - planning needed")
                return True
            
            # Check if plan is outdated (more than 6 hours old)
            plan_age_hours = (datetime.now() - current_plan.updated_at).total_seconds() / 3600
            if plan_age_hours > 6:
                logger.info(f"🎯 {agent.name}'s plan is {plan_age_hours:.1f} hours old - updating needed")
                return True
                
            # Check if agent has had significant experiences since last plan
            recent_memories = await self.memory_manager.get_recent_memories(
                agent.id, 
                since=current_plan.updated_at,
                limit=20
            )
            
            if recent_memories:
                high_importance_memories = [m for m in recent_memories if m.importance_score >= 7.0]
                if len(high_importance_memories) >= 3:
                    logger.info(f"🎯 {agent.name} has {len(high_importance_memories)} high-importance experiences - plan update needed")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking planning trigger for {agent.name}: {e}")
            return False
    
    async def generate_daily_plan(self, agent: Agent) -> Optional[DailyPlan]:
        """Generate a comprehensive daily plan for an agent using LLM reasoning.
        
        Args:
            agent: The agent to generate a plan for
            
        Returns:
            Generated daily plan or None if generation failed
        """
        try:
            logger.info(f"🎯 COGNITIVE PROCESS: Generating daily plan for {agent.name}")
            
            # Get relevant context for planning
            planning_context = await self._build_planning_context(agent)
            
            # Generate plan using LLM
            plan_data = await self._generate_llm_plan(agent, planning_context)
            
            if not plan_data:
                logger.warning(f"Failed to generate plan data for {agent.name}")
                return None
            
            # Convert LLM response to structured plan
            daily_plan = await self._parse_plan_response(agent, plan_data)
            
            if daily_plan:
                # Store the plan
                await self._store_daily_plan(daily_plan)
                
                logger.info(f"📋 PLAN GENERATED: Created daily plan for {agent.name} with {len(daily_plan.hourly_blocks)} blocks")
                return daily_plan
            else:
                logger.warning(f"Failed to parse plan response for {agent.name}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to generate daily plan for {agent.name}: {e}")
            return None
    
    async def get_current_daily_plan(self, agent_id: str) -> Optional[DailyPlan]:
        """Get the current daily plan for an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Current daily plan or None if no plan exists
        """
        try:
            today = date.today()
            plans = await self.sqlite_store.get_plans(
                agent_id=agent_id,
                plan_type="daily",
                date_for=today,
                limit=1
            )
            
            if plans:
                plan_data = plans[0]
                return DailyPlan.model_validate_json(plan_data["content"])
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving daily plan for {agent_id}: {e}")
            return None
    
    async def get_current_task(self, agent_id: str) -> Optional[Task]:
        """Get the current task the agent should be working on.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Current task or None if no task is active
        """
        try:
            current_plan = await self.get_current_daily_plan(agent_id)
            if not current_plan:
                return None
            
            # Find the current hourly block based on time
            current_time = datetime.now().time()
            current_block = None
            
            for block in current_plan.hourly_blocks:
                if (block.start_time <= current_time <= block.end_time and 
                    block.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]):
                    current_block = block
                    break
            
            if not current_block:
                return None
            
            # Find the current task within the block
            for task in current_block.tasks:
                if task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
                    return task
            
            # If no specific task, create a general task for the block
            general_task = Task(
                description=current_block.activity,
                action_type=ActionType.WAIT,  # Default action
                duration_minutes=current_block.duration_minutes,
                location=current_block.location
            )
            
            return general_task
            
        except Exception as e:
            logger.error(f"Error getting current task for {agent_id}: {e}")
            return None
    
    async def update_task_status(self, agent_id: str, task_id: str, status: TaskStatus) -> bool:
        """Update the status of a specific task.
        
        Args:
            agent_id: ID of the agent
            task_id: ID of the task to update
            status: New status for the task
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            current_plan = await self.get_current_daily_plan(agent_id)
            if not current_plan:
                return False
            
            # Find and update the task
            task_updated = False
            for block in current_plan.hourly_blocks:
                for task in block.tasks:
                    if str(task.id) == task_id:
                        task.status = status
                        task_updated = True
                        break
                if task_updated:
                    break
            
            if task_updated:
                # Update the plan in storage
                await self._store_daily_plan(current_plan)
                logger.info(f"📋 Task {task_id} for {agent_id} updated to {status.value}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating task status for {agent_id}: {e}")
            return False
    
    async def _build_planning_context(self, agent: Agent) -> Dict:
        """Build context for LLM planning.
        
        Args:
            agent: The agent to build context for
            
        Returns:
            Dictionary with planning context
        """
        # Get recent memories for context
        recent_memories = await self.memory_manager.get_recent_memories(
            agent.id, 
            limit=15
        )
        
        # Get reflections for deeper insights
        recent_reflections = [m for m in recent_memories if m.memory_type.value == "reflection"]
        
        # Build context
        return {
            "agent": agent,
            "current_time": datetime.now().strftime("%H:%M"),
            "current_date": date.today().strftime("%Y-%m-%d"),
            "recent_memories": recent_memories[:10],  # Most recent 10
            "recent_reflections": recent_reflections[:3],  # Most recent 3 reflections
            "personality_traits": agent.personality.split(", ") if agent.personality else [],
            "current_location": agent.state.current_location or agent.home_location,
            "energy_level": agent.state.energy,
            "mood_level": agent.state.mood
        }
    
    async def _generate_llm_plan(self, agent: Agent, context: Dict) -> Optional[Dict]:
        """Generate plan using LLM with structured prompting.
        
        Args:
            agent: The agent to plan for
            context: Planning context
            
        Returns:
            Dictionary with plan components or None if failed
        """
        prompt = self._build_planning_prompt(agent, context)
        
        logger.info(f"🎯 COGNITIVE PROCESS: {agent.name} is creating a daily plan")
        
        try:
            response = await self.llm_service.ollama_client.generate(
                model=self.llm_service.settings.ollama_model,
                prompt=prompt,
                options={
                    "temperature": 0.7,  # Allow creativity but stay focused
                    "top_p": 0.9,
                    "num_predict": 800  # Allow longer responses for detailed planning
                }
            )
            
            # Parse the LLM response
            plan_data = self._parse_llm_planning_response(response.response)
            
            logger.info(f"📋 PLAN COMPLETE: {agent.name} created daily plan with {len(plan_data.get('blocks', []))} time blocks")
            return plan_data
            
        except Exception as e:
            logger.error(f"LLM plan generation failed for {agent.name}: {e}")
            return None
    
    def _build_planning_prompt(self, agent: Agent, context: Dict) -> str:
        """Build structured prompt for LLM plan generation.
        
        Args:
            agent: The agent to plan for
            context: Planning context
            
        Returns:
            Formatted prompt string
        """
        # Format recent experiences
        memory_context = ""
        if context["recent_memories"]:
            memory_context = "Recent experiences:\n" + "\n".join([
                f"- {memory.content[:100]}..."
                for memory in context["recent_memories"][:5]
            ])
        
        # Format reflections
        reflection_context = ""
        if context["recent_reflections"]:
            reflection_context = "Recent insights:\n" + "\n".join([
                f"- {reflection.content[:150]}..."
                for reflection in context["recent_reflections"][:2]
            ])
        
        prompt = f"""You are {agent.name}, planning your day.

Your profile:
- Bio: {agent.bio}
- Personality: {agent.personality}
- Current location: {context["current_location"]}
- Energy: {context["energy_level"]:.1f}/100
- Mood: {context["mood_level"]:.1f}/10

{memory_context}

{reflection_context}

It's {context["current_time"]} on {context["current_date"]}. Create a realistic daily plan that fits your personality and current situation.

Consider:
- Your personality traits and natural preferences
- Your recent experiences and how they might influence today
- Your energy and mood levels
- Realistic activities you can do in your environment
- Social connections and relationships you might want to nurture

Format your response as:

GOAL: [One sentence describing your main goal for today]

MORNING: [Time block like "09:00-12:00"]
Activity: [What you'll do]
Location: [Where you'll be]
Reasoning: [Why this fits your personality and situation]

AFTERNOON: [Time block like "13:00-17:00"]
Activity: [What you'll do]
Location: [Where you'll be]
Reasoning: [Why this fits your personality and situation]

EVENING: [Time block like "18:00-21:00"]
Activity: [What you'll do]
Location: [Where you'll be]
Reasoning: [Why this fits your personality and situation]

Keep activities realistic and specific to your character and environment."""
        
        return prompt
    
    def _parse_llm_planning_response(self, response: str) -> Dict:
        """Parse LLM response into structured plan data.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Dictionary with parsed plan components
        """
        try:
            plan_data = {
                "goal": "",
                "blocks": []
            }
            
            # Extract goal
            goal_match = re.search(r"GOAL:\s*(.+)", response, re.IGNORECASE)
            if goal_match:
                plan_data["goal"] = goal_match.group(1).strip()
            
            # Extract time blocks
            block_pattern = r"(MORNING|AFTERNOON|EVENING):\s*\[?([^\]]+)\]?\s*\nActivity:\s*(.+)\s*\nLocation:\s*(.+)\s*\nReasoning:\s*(.+?)(?=\n\n|\n[A-Z]|$)"
            
            blocks = re.findall(block_pattern, response, re.IGNORECASE | re.DOTALL)
            
            for period, time_range, activity, location, reasoning in blocks:
                # Parse time range
                start_time, duration = self._parse_time_range(time_range.strip())
                
                block_data = {
                    "period": period.lower(),
                    "start_time": start_time,
                    "duration_minutes": duration,
                    "activity": activity.strip(),
                    "location": location.strip(),
                    "reasoning": reasoning.strip()
                }
                
                plan_data["blocks"].append(block_data)
            
            return plan_data
            
        except Exception as e:
            logger.error(f"Error parsing LLM planning response: {e}")
            return {"goal": "Have a good day", "blocks": []}
    
    def _parse_time_range(self, time_range: str) -> Tuple[time, int]:
        """Parse time range string into start time and duration.
        
        Args:
            time_range: String like "09:00-12:00" or "morning"
            
        Returns:
            Tuple of (start_time, duration_minutes)
        """
        try:
            # Default time mappings for periods
            default_times = {
                "morning": (time(9, 0), 180),    # 9 AM - 12 PM (3 hours)
                "afternoon": (time(13, 0), 240), # 1 PM - 5 PM (4 hours)
                "evening": (time(18, 0), 180)    # 6 PM - 9 PM (3 hours)
            }
            
            # Check for explicit time range
            time_match = re.search(r"(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})", time_range)
            if time_match:
                start_hour, start_min, end_hour, end_min = map(int, time_match.groups())
                start_time = time(start_hour, start_min)
                end_time = time(end_hour, end_min)
                
                # Calculate duration
                start_dt = datetime.combine(date.today(), start_time)
                end_dt = datetime.combine(date.today(), end_time)
                if end_dt < start_dt:  # Next day
                    end_dt += timedelta(days=1)
                
                duration = int((end_dt - start_dt).total_seconds() / 60)
                return start_time, duration
            
            # Check for period names
            for period, (default_start, default_duration) in default_times.items():
                if period in time_range.lower():
                    return default_start, default_duration
            
            # Fallback to afternoon
            return default_times["afternoon"]
            
        except Exception as e:
            logger.error(f"Error parsing time range '{time_range}': {e}")
            return time(12, 0), 120  # Default: noon for 2 hours
    
    async def _parse_plan_response(self, agent: Agent, plan_data: Dict) -> Optional[DailyPlan]:
        """Convert parsed plan data into DailyPlan object.
        
        Args:
            agent: The agent this plan is for
            plan_data: Parsed plan data from LLM
            
        Returns:
            DailyPlan object or None if parsing failed
        """
        try:
            # Create hourly blocks
            hourly_blocks = []
            for block_data in plan_data.get("blocks", []):
                # Create a general task for this block
                task = Task(
                    description=block_data["activity"],
                    action_type=self._infer_action_type(block_data["activity"]),
                    duration_minutes=block_data["duration_minutes"],
                    location=block_data.get("location")
                )
                
                hourly_block = HourlyBlock(
                    start_time=block_data["start_time"],
                    duration_minutes=block_data["duration_minutes"],
                    activity=block_data["activity"],
                    location=block_data.get("location"),
                    tasks=[task]
                )
                
                hourly_blocks.append(hourly_block)
            
            # Create daily plan
            daily_plan = DailyPlan(
                agent_id=agent.id,
                date=date.today(),
                goals=[plan_data.get("goal", "Have a productive day")],
                hourly_blocks=hourly_blocks
            )
            
            return daily_plan
            
        except Exception as e:
            logger.error(f"Error parsing plan response for {agent.name}: {e}")
            return None
    
    def _infer_action_type(self, activity_description: str) -> ActionType:
        """Infer action type from activity description.
        
        Args:
            activity_description: Description of the activity
            
        Returns:
            Inferred ActionType
        """
        activity_lower = activity_description.lower()
        
        # Movement-related activities
        if any(word in activity_lower for word in ["go to", "visit", "travel", "move", "walk"]):
            return ActionType.MOVE
        
        # Interaction activities
        if any(word in activity_lower for word in ["talk", "meet", "interact", "socialize", "chat"]):
            return ActionType.SAY
        
        # Object interaction
        if any(word in activity_lower for word in ["use", "work with", "operate", "handle"]):
            return ActionType.INTERACT
        
        # Reflection activities
        if any(word in activity_lower for word in ["think", "reflect", "plan", "contemplate"]):
            return ActionType.REFLECT
        
        # Default to wait (general activity)
        return ActionType.WAIT
    
    async def _store_daily_plan(self, daily_plan: DailyPlan) -> None:
        """Store daily plan in database.
        
        Args:
            daily_plan: The plan to store
        """
        try:
            await self.sqlite_store.add_plan(
                plan_id=str(daily_plan.id),
                agent_id=daily_plan.agent_id,
                plan_type="daily",
                content=daily_plan.model_dump_json(),
                date_for=daily_plan.date,
                status=daily_plan.status.value
            )
            
        except Exception as e:
            logger.error(f"Error storing daily plan: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Perform health check on planning engine.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Test LLM service
            if not await self.llm_service.health_check():
                return False
            
            # Test memory manager
            if not await self.memory_manager.health_check():
                return False
            
            # Test database connection
            if not await self.sqlite_store.health_check():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Planning engine health check failed: {e}")
            return False
