"""Main simulation controller that orchestrates all components."""

import asyncio
import logging
from typing import Dict, List, Optional

from ..agents.memory_manager import MemoryManager
from ..agents.reflection_engine import ReflectionEngine
from ..agents.planning_engine import PlanningEngine
from ..config import get_settings
from ..config.agent_config import AgentConfigLoader
from ..config.world_config import WorldConfigLoader
from ..logging.simulation_logger import SimulationLogger
from ..models.agent import Agent
from ..storage.sqlite_store import SQLiteStore
from ..storage.vector_store import VectorStore
from .action_executor import ActionExecutor
from .llm_behavior import LLMBehavior
from ..llm.llm_service import LLMService
from .time_manager import TimeManager
from .world_manager import WorldManager

logger = logging.getLogger(__name__)


class SimulationController:
    """Main controller for the agent simulation."""
    
    def __init__(self, session_name: Optional[str] = None):
        """Initialize simulation controller.
        
        Args:
            session_name: Name for this simulation session
        """
        self.settings = get_settings()
        
        # Beautiful logging system
        self.sim_logger = SimulationLogger(session_name)
        
        # Core components
        self.storage = SQLiteStore(self.settings.sqlite_db_path)
        self.vector_store = VectorStore()
        self.world_config_loader = WorldConfigLoader(self.settings.world_config_path)
        self.agent_config_loader = AgentConfigLoader(self.settings.agents_config_path)
        
        # Simulation components
        self.world_manager = WorldManager(self.world_config_loader, self.storage)
        self.time_manager = TimeManager(self.settings.tick_duration_minutes)
        self.action_executor = ActionExecutor(self.world_manager)
        self.llm_service = LLMService(self.settings)
        
        # Memory system
        self.memory_manager = MemoryManager(self.storage, self.vector_store, self.llm_service)
        
        # Reflection system
        self.reflection_engine = ReflectionEngine(
            self.memory_manager, self.storage, self.llm_service, self.settings
        )
        
        # Planning system
        self.planning_engine = PlanningEngine(
            self.memory_manager, self.storage, self.llm_service, self.settings
        )
        
        # Behavior system with memory and planning integration
        self.behavior_system = LLMBehavior(
            self.world_manager, 
            self.llm_service, 
            self.memory_manager, 
            self.planning_engine
        )
        
        # State
        self.agents: Dict[str, Agent] = {}
        self.is_initialized = False
        
        # Setup tick callback
        self.time_manager.add_tick_callback(self._on_tick)
    
    async def initialize(self) -> None:
        """Initialize the simulation."""
        if self.is_initialized:
            logger.warning("Simulation already initialized")
            return
        
        logger.info("Initializing simulation...")
        
        # Initialize storage
        await self.storage.initialize_schema()
        
        # Initialize vector store
        self.vector_store.initialize_collections()
        
        # Initialize world
        await self.world_manager.initialize()
        
        # Load and create agents
        await self._load_agents()
        
        self.is_initialized = True
        logger.info(f"Simulation initialized with {len(self.agents)} agents")
        
        # Log beautiful simulation start
        world_summary = self.world_manager.get_world_summary()
        self.sim_logger.log_simulation_start(len(self.agents), world_summary)
    
    async def _load_agents(self) -> None:
        """Load agents from configuration."""
        agents_from_config = self.agent_config_loader.load_agents()
        
        for agent in agents_from_config:
            # Agent is already created from config
            
            # Check if agent already exists in database
            existing_agent = await self.storage.get_agent(agent.id)
            if existing_agent:
                # Use existing agent
                self.agents[agent.id] = existing_agent
                logger.debug(f"Loaded existing agent: {agent.name}")
            else:
                # Create new agent
                await self.storage.create_agent(agent)
                self.agents[agent.id] = agent
                logger.debug(f"Created new agent: {agent.name}")
            
            # Place agent in world if not already placed
            current_location = self.world_manager.get_agent_location(agent.id)
            if not current_location:
                await self.world_manager.place_agent(agent.id, agent.home_location)
                logger.debug(f"Placed {agent.name} at {agent.home_location}")
    
    async def start_simulation(self) -> None:
        """Start the simulation."""
        if not self.is_initialized:
            await self.initialize()
        
        logger.info("Starting simulation...")
        await self.time_manager.start_simulation()
    
    async def pause_simulation(self) -> None:
        """Pause the simulation."""
        logger.info("Pausing simulation...")
        await self.time_manager.pause_simulation()
    
    async def step_simulation(self) -> None:
        """Advance simulation by one tick."""
        if not self.is_initialized:
            await self.initialize()
        
        logger.info("Stepping simulation...")
        await self.time_manager.advance_tick()
    
    async def _on_tick(self, tick: int) -> None:
        """Called on each simulation tick.
        
        Args:
            tick: Current tick number
        """
        logger.debug(f"Processing tick {tick}")
        
        # Log beautiful tick start
        elapsed_minutes = tick * self.settings.tick_duration_minutes
        self.sim_logger.log_tick_start(tick, elapsed_minutes)
        
        # Process each agent
        for agent in self.agents.values():
            try:
                await self._process_agent_tick(agent, tick)
            except Exception as e:
                logger.error(f"Error processing agent {agent.name} on tick {tick}: {e}")
        
        # Get current agent summaries for beautiful logging
        agent_summaries = {}
        for agent_id, agent in self.agents.items():
            location = self.world_manager.get_agent_location(agent_id)
            place_info = self.world_manager.get_place_info(location) if location else None
            
            # Get planning information for the agent
            planning_info = {"has_plan": False}
            try:
                current_plan = await self.planning_engine.get_current_daily_plan(agent_id)
                current_task = await self.planning_engine.get_current_task(agent_id)
                
                planning_info = {
                    "has_plan": current_plan is not None,
                    "current_goal": current_plan.goals[0] if current_plan and current_plan.goals else None,
                    "current_task": current_task.description if current_task else None,
                    "current_task_location": current_task.location if current_task else None,
                    "plan_blocks_count": len(current_plan.hourly_blocks) if current_plan else 0
                }
            except Exception as e:
                planning_info = {"error": str(e)}
            
            agent_summaries[agent_id] = {
                "name": agent.name,
                "location": location,
                "location_name": place_info["name"] if place_info else "unknown",
                "energy": agent.state.energy,
                "mood": agent.state.mood,
                "status": agent.state.status.value if hasattr(agent.state.status, 'value') else str(agent.state.status),
                "planning": planning_info
            }
        
        # Log beautiful tick completion
        self.sim_logger.log_tick_complete(agent_summaries)
        
        logger.info(f"[{self.time_manager.format_tick_time(tick)}] Tick complete")
    
    async def _process_agent_tick(self, agent: Agent, tick: int) -> None:
        """Process one agent for a tick.
        
        Args:
            agent: Agent to process
            tick: Current tick number
        """
        try:
            # Get current context for thinking display
            current_location = self.world_manager.get_agent_location(agent.id)
            place_info = self.world_manager.get_place_info(current_location) if current_location else None
            available_actions = self.action_executor.get_available_actions(agent.id)
            
            # Choose action using LLM-powered behavior with real reasoning
            action, reasoning = await self.behavior_system.choose_action_with_reasoning(agent)
            action.agent_id = agent.id  # Ensure correct agent ID
            
            # Show the agent's thinking process
            action_type_str = action.action_type.value if hasattr(action.action_type, 'value') else str(action.action_type)
            location_name = place_info["name"] if place_info else current_location or "unknown"
            
            self.sim_logger.log_agent_thinking(
                agent.name,
                location_name,
                available_actions,
                action_type_str,
                reasoning
            )
            
            # Execute the action
            result = await self.action_executor.execute_action(action)
            
            # Prepare metadata for beautiful logging
            metadata = {
                "location": location_name,
                "energy": agent.state.energy,
                "mood": agent.state.mood,
                **result.side_effects
            }
            
            # Log action result with beautiful Apple-style UX
            self.sim_logger.log_agent_action(
                agent.name,
                action_type_str,
                result.message,
                result.success,
                metadata
            )
            
            # Still log to standard logger for debugging
            if result.success:
                logger.info(f"[{self.time_manager.format_tick_time(tick)}] {agent.name}: {result.message}")
            else:
                logger.warning(f"[{self.time_manager.format_tick_time(tick)}] {agent.name}: Failed - {result.message}")
            
            # M3: Form memory from this action
            try:
                memory = await self.memory_manager.form_memory_from_action(
                    agent, action, result, location_name
                )
                logger.debug(f"Formed memory for {agent.name}: {memory.content[:50]}... (importance: {memory.importance_score:.1f})")
                
                # M4: Update importance accumulator and check for reflection trigger
                await self.reflection_engine.update_importance_accumulator(agent, memory.importance_score)
                
                # Check if agent should reflect
                if await self.reflection_engine.should_reflect(agent):
                    logger.info(f"Triggering reflection for {agent.name} (accumulated importance: {agent.state.importance_accumulator:.1f})")
                    reflections = await self.reflection_engine.trigger_reflection(agent)
                    
                    if reflections:
                        # Log reflection beautifully
                        self.sim_logger.log_agent_reflection(
                            agent.name,
                            len(reflections),
                            [r.content for r in reflections]
                        )
                        logger.info(f"Generated {len(reflections)} reflections for {agent.name}")
                
            except Exception as e:
                logger.error(f"Failed to form memory for {agent.name}: {e}")
            
            # M5: Check if agent should update their daily plan
            try:
                if await self.planning_engine.should_plan(agent):
                    logger.info(f"Triggering daily planning for {agent.name}")
                    daily_plan = await self.planning_engine.generate_daily_plan(agent)
                    
                    if daily_plan:
                        # Create plan summary for beautiful logging
                        plan_summary = self._create_plan_summary(daily_plan)
                        
                        # Log plan generation with detailed summary
                        self.sim_logger.log_agent_planning(agent.name, len(daily_plan.hourly_blocks), plan_summary)
                        logger.info(f"Generated daily plan for {agent.name} with {len(daily_plan.hourly_blocks)} time blocks")
                        
            except Exception as e:
                logger.error(f"Failed to generate plan for {agent.name}: {e}")
        except Exception as e:
            logger.error(f"Error in _process_agent_tick for {agent.name}: {e}")
            # Log error beautifully too
            self.sim_logger.log_agent_action(
                agent.name,
                "error",
                f"Action failed: {str(e)}",
                False,
                {"location": "unknown", "energy": agent.state.energy}
            )
    
    
    def get_simulation_status(self) -> Dict:
        """Get current simulation status.
        
        Returns:
            Dictionary with simulation status
        """
        if not self.is_initialized:
            return {
                "status": "not_initialized",
                "message": "Simulation not initialized"
            }
        
        time_status = self.time_manager.get_status()
        world_summary = self.world_manager.get_world_summary()
        
        # Get agent summaries
        agent_summaries = {}
        for agent_id, agent in self.agents.items():
            location = self.world_manager.get_agent_location(agent_id)
            place_info = self.world_manager.get_place_info(location) if location else None
            
            agent_summaries[agent_id] = {
                "name": agent.name,
                "location": location,
                "location_name": place_info["name"] if place_info else "unknown",
                "energy": agent.state.energy,
                "status": agent.state.status.value if hasattr(agent.state.status, 'value') else str(agent.state.status)
            }
        
        return {
            "status": "running" if time_status["is_running"] else "paused",
            "time": time_status,
            "world": world_summary,
            "agents": agent_summaries,
            "total_agents": len(self.agents)
        }
    
    def get_agent_details(self, agent_id: str, log_beautifully: bool = False) -> Optional[Dict]:
        """Get detailed information about an agent.
        
        Args:
            agent_id: ID of the agent
            log_beautifully: Whether to display with beautiful Apple-style logging
            
        Returns:
            Agent details or None if not found
        """
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        
        location = self.world_manager.get_agent_location(agent_id)
        place_info = self.world_manager.get_place_info(location) if location else None
        
        details = {
            "id": agent.id,
            "name": agent.name,
            "bio": agent.bio,
            "personality": agent.personality,
            "home_location": agent.home_location,
            "current_location": location,
            "current_location_name": place_info["name"] if place_info else "unknown",
            "state": {
                "status": agent.state.status.value if hasattr(agent.state.status, 'value') else str(agent.state.status),
                "energy": agent.state.energy,
                "mood": agent.state.mood,
                "current_task": agent.state.current_task
            },
            "available_actions": self.action_executor.get_available_actions(agent_id)
        }
        
        # Add planning information
        try:
            # Note: These are synchronous calls for display purposes
            # The actual planning engine uses async methods
            details["planning"] = {
                "has_plan": False,
                "current_goal": None,
                "current_activity": None,
                "current_location_matches_plan": False,
                "time_block_status": None
            }
        except Exception as e:
            # Don't fail if planning info is unavailable
            details["planning"] = {"error": str(e)}
        
        # Log beautifully if requested
        if log_beautifully:
            self.sim_logger.log_agent_detail(details)
        
        return details
    
    def _create_plan_summary(self, daily_plan) -> str:
        """Create a beautiful summary of the daily plan for logging.
        
        Args:
            daily_plan: DailyPlan object
            
        Returns:
            Formatted plan summary string
        """
        summary_parts = []
        
        # Add goals
        if daily_plan.goals:
            goals_text = " & ".join(daily_plan.goals[:2])  # Show first 2 goals
            if len(daily_plan.goals) > 2:
                goals_text += f" + {len(daily_plan.goals) - 2} more"
            summary_parts.append(f"🎯 Goals: {goals_text}")
        
        # Add time blocks summary
        if daily_plan.hourly_blocks:
            time_blocks = []
            for block in daily_plan.hourly_blocks[:2]:  # Show first 2 blocks
                time_range = f"{block.start_time.strftime('%H:%M')}-{block.end_time.strftime('%H:%M')}"
                activity = block.activity[:40] + "..." if len(block.activity) > 40 else block.activity
                time_blocks.append(f"{time_range}: {activity}")
            
            if len(daily_plan.hourly_blocks) > 2:
                time_blocks.append(f"... + {len(daily_plan.hourly_blocks) - 2} more blocks")
            
            summary_parts.append(f"📅 Schedule:\n" + "\n".join(f"   • {block}" for block in time_blocks))
        
        # Add current task if available
        if daily_plan.hourly_blocks:
            current_block = daily_plan.hourly_blocks[0]  # Assume first block is current
            if current_block.tasks:
                current_task = current_block.tasks[0]
                task_desc = current_task.description[:30] + "..." if len(current_task.description) > 30 else current_task.description
                summary_parts.append(f"📌 Next up: {task_desc}")
        
        return "\n\n".join(summary_parts)
    
    def export_simulation_data(self) -> Dict[str, str]:
        """Export current simulation data for analysis.
        
        Returns:
            Dictionary of exported file paths
        """
        if not self.is_initialized:
            return {}
        
        # Export data with beautiful summary
        return self.sim_logger.export_current_data()
    
    async def cleanup(self) -> None:
        """Clean up simulation resources."""
        logger.info("Cleaning up simulation...")
        
        # Stop simulation
        if self.time_manager.is_running:
            await self.time_manager.pause_simulation()
        
        # Export final data if there's any simulation activity
        if self.sim_logger.get_logged_data().get('agent_actions'):
            total_ticks = self.time_manager.current_tick
            self.sim_logger.log_simulation_end(total_ticks)
        
        # Close storage
        await self.storage.disconnect()
        
        logger.info("Simulation cleanup complete")
