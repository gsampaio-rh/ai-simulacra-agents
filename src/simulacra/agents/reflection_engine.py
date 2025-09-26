"""Reflection engine for generating LLM-powered insights from agent memories."""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from ..config.settings import Settings
from ..llm.llm_service import LLMService
from ..models.agent import Agent
from ..models.memory import Memory, MemoryType, Reflection
from ..storage.sqlite_store import SQLiteStore
from .memory_manager import MemoryManager

logger = logging.getLogger(__name__)


class ReflectionEngine:
    """Generates high-level insights and reflections from agent memories."""
    
    def __init__(
        self,
        memory_manager: MemoryManager,
        sqlite_store: SQLiteStore,
        llm_service: LLMService,
        settings: Optional[Settings] = None
    ):
        """Initialize reflection engine.
        
        Args:
            memory_manager: Memory manager for retrieving memories
            sqlite_store: SQLite store for persisting reflections
            llm_service: LLM service for generating insights
            settings: Application settings (will create if None)
        """
        self.memory_manager = memory_manager
        self.sqlite_store = sqlite_store
        self.llm_service = llm_service
        self.settings = settings or Settings()
    
    async def should_reflect(self, agent: Agent) -> bool:
        """Check if an agent should generate reflections based on importance accumulation.
        
        Args:
            agent: The agent to check
            
        Returns:
            True if agent should reflect, False otherwise
        """
        try:
            # Check if importance accumulator exceeds threshold
            return agent.state.importance_accumulator >= self.settings.reflection_threshold
        except Exception as e:
            logger.error(f"Error checking reflection trigger for {agent.name}: {e}")
            return False
    
    async def trigger_reflection(self, agent: Agent) -> List[Reflection]:
        """Trigger reflection process for an agent.
        
        Args:
            agent: The agent to generate reflections for
            
        Returns:
            List of generated reflections
        """
        try:
            logger.info(f"Triggering reflection for {agent.name} (importance: {agent.state.importance_accumulator:.1f})")
            
            # Get recent high-importance memories for reflection
            memories = await self._get_reflection_memories(agent)
            
            if not memories:
                logger.warning(f"No memories found for reflection for {agent.name}")
                return []
            
            # Generate reflection insights using LLM
            insights = await self.llm_service.generate_reflection(agent, memories, max_insights=3)
            
            if not insights:
                logger.warning(f"No insights generated for {agent.name}")
                return []
            
            # Convert insights to Reflection objects
            reflections = []
            for insight in insights:
                reflection = await self._create_reflection(agent, insight, memories)
                reflections.append(reflection)
            
            # Store reflections as high-importance memories
            for reflection in reflections:
                await self._store_reflection_as_memory(reflection)
            
            # Reset importance accumulator
            await self._reset_importance_accumulator(agent)
            
            # Update agent's reflection time and count
            await self._update_reflection_metadata(agent, len(reflections))
            
            logger.info(f"Generated {len(reflections)} reflections for {agent.name}")
            return reflections
            
        except Exception as e:
            logger.error(f"Failed to generate reflections for {agent.name}: {e}")
            return []
    
    async def get_agent_reflections(
        self, 
        agent_id: str, 
        limit: int = 10
    ) -> List[Reflection]:
        """Get recent reflections for an agent.
        
        Args:
            agent_id: ID of the agent
            limit: Maximum number of reflections to retrieve
            
        Returns:
            List of reflections
        """
        try:
            return await self.sqlite_store.get_agent_reflections(agent_id, limit)
        except Exception as e:
            logger.error(f"Failed to get reflections for {agent_id}: {e}")
            return []
    
    async def update_importance_accumulator(self, agent: Agent, importance_delta: float) -> None:
        """Update agent's importance accumulator.
        
        Args:
            agent: The agent to update
            importance_delta: Amount to add to accumulator
        """
        try:
            agent.state.importance_accumulator += importance_delta
            
            # Update in database
            await self.sqlite_store.update_agent_state(agent.state)
            
            logger.debug(f"Updated importance accumulator for {agent.name}: {agent.state.importance_accumulator:.1f} (+{importance_delta:.1f})")
            
        except Exception as e:
            logger.error(f"Failed to update importance accumulator for {agent.name}: {e}")
    
    async def _get_reflection_memories(self, agent: Agent) -> List[Memory]:
        """Get memories suitable for reflection.
        
        Args:
            agent: The agent to get memories for
            
        Returns:
            List of memories for reflection
        """
        try:
            # Get recent memories since last reflection
            recent_memories = await self.memory_manager.get_recent_memories(
                agent.id,
                limit=50,  # Get more memories for richer reflection
                hours=72   # Look back 3 days max
            )
            
            # Filter out reflection memories (don't reflect on reflections)
            non_reflection_memories = [
                memory for memory in recent_memories
                if memory.memory_type != MemoryType.REFLECTION
            ]
            
            # Sort by importance and get top memories
            important_memories = sorted(
                non_reflection_memories,
                key=lambda m: m.importance_score,
                reverse=True
            )[:20]  # Top 20 most important memories
            
            return important_memories
            
        except Exception as e:
            logger.error(f"Failed to get reflection memories for {agent.name}: {e}")
            return []
    
    async def _create_reflection(
        self, 
        agent: Agent, 
        insight: str, 
        supporting_memories: List[Memory]
    ) -> Reflection:
        """Create a reflection object from an insight.
        
        Args:
            agent: The agent generating the reflection
            insight: The insight text
            supporting_memories: Memories that support this insight
            
        Returns:
            Created reflection
        """
        # Clean up insight text (remove numbering if present)
        clean_insight = insight.strip()
        if clean_insight.startswith(('1.', '2.', '3.', '4.', '5.')):
            clean_insight = clean_insight.split('.', 1)[1].strip()
        
        reflection = Reflection(
            id=uuid4(),
            agent_id=agent.id,
            content=clean_insight,
            supporting_memories=[memory.id for memory in supporting_memories],
            timestamp=datetime.utcnow(),
            importance_score=8.0  # Reflections are inherently high importance
        )
        
        return reflection
    
    async def _store_reflection_as_memory(self, reflection: Reflection) -> None:
        """Store reflection as a high-importance memory.
        
        Args:
            reflection: The reflection to store
        """
        try:
            # Store reflection in reflections table
            await self.sqlite_store.add_reflection(reflection)
            
            # Also create a memory entry for this reflection
            reflection_memory = Memory(
                agent_id=reflection.agent_id,
                content=f"I reflected and realized: {reflection.content}",
                memory_type=MemoryType.REFLECTION,
                timestamp=reflection.timestamp,
                importance_score=reflection.importance_score,
                location=None  # Reflections are internal
            )
            
            # Store the reflection memory (this will also generate embeddings)
            await self.memory_manager._store_memory(reflection_memory)
            
            logger.debug(f"Stored reflection as memory: {reflection.content[:50]}...")
            
        except Exception as e:
            logger.error(f"Failed to store reflection as memory: {e}")
            raise
    
    async def _reset_importance_accumulator(self, agent: Agent) -> None:
        """Reset agent's importance accumulator after reflection.
        
        Args:
            agent: The agent to reset
        """
        try:
            agent.state.importance_accumulator = 0.0
            await self.sqlite_store.update_agent_state(agent.state)
            
            logger.debug(f"Reset importance accumulator for {agent.name}")
            
        except Exception as e:
            logger.error(f"Failed to reset importance accumulator for {agent.name}: {e}")
    
    async def _update_reflection_metadata(self, agent: Agent, reflection_count: int) -> None:
        """Update agent's reflection metadata.
        
        Args:
            agent: The agent to update
            reflection_count: Number of reflections generated
        """
        try:
            # Update reflection time and count
            agent.state.last_reflection_time = datetime.utcnow()
            agent.reflections_count += reflection_count
            
            # Update in database
            await self.sqlite_store.update_agent_state(agent.state)
            # Note: Agent reflection count is updated in-memory for now
            # TODO: Add update_agent method to SQLiteStore if needed
            
            logger.debug(f"Updated reflection metadata for {agent.name}: total {agent.reflections_count} reflections")
            
        except Exception as e:
            logger.error(f"Failed to update reflection metadata for {agent.name}: {e}")
    
    async def health_check(self) -> bool:
        """Check if reflection engine is working.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Test dependencies
            memory_healthy = await self.memory_manager.health_check()
            llm_healthy = await self.llm_service.health_check()
            
            return memory_healthy and llm_healthy
            
        except Exception as e:
            logger.warning(f"Reflection engine health check failed: {e}")
            return False
