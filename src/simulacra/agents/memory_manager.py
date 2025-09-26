"""Memory management system for agents with formation, storage, and retrieval."""

import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from ..llm.llm_service import LLMService
from ..models.action import Action, ActionResult
from ..models.agent import Agent
from ..models.memory import Memory, MemoryType, MemoryQuery, MemorySearchResult
from ..storage.sqlite_store import SQLiteStore
from ..storage.vector_store import VectorStore

logger = logging.getLogger(__name__)


class MemoryManager:
    """Manages memory formation, storage, and retrieval for agents."""
    
    def __init__(
        self, 
        sqlite_store: SQLiteStore, 
        vector_store: VectorStore,
        llm_service: LLMService
    ):
        """Initialize memory manager.
        
        Args:
            sqlite_store: SQLite storage for memory metadata
            vector_store: Vector storage for semantic search
            llm_service: LLM service for importance scoring
        """
        self.sqlite_store = sqlite_store
        self.vector_store = vector_store
        self.llm_service = llm_service
    
    async def form_memory_from_action(
        self, 
        agent: Agent, 
        action: Action, 
        result: ActionResult,
        location: str
    ) -> Memory:
        """Form a memory from an agent's action and its result.
        
        Args:
            agent: The agent performing the action
            action: The action performed
            result: The result of the action
            location: Where the action took place
            
        Returns:
            Created memory
        """
        # Create memory content based on action and result
        content = self._create_action_memory_content(agent, action, result, location)
        
        # Score importance using LLM
        importance = await self._score_memory_importance(agent, content)
        
        # Create memory
        memory = Memory(
            agent_id=agent.id,
            content=content,
            memory_type=MemoryType.ACTION,
            importance_score=importance,
            location=location
        )
        
        # Store memory
        await self._store_memory(memory)
        
        logger.debug(f"Formed action memory for {agent.name}: {content[:50]}... (importance: {importance:.1f})")
        return memory
    
    async def form_memory_from_observation(
        self,
        agent: Agent,
        observation: str,
        location: str
    ) -> Memory:
        """Form a memory from an agent's observation.
        
        Args:
            agent: The agent making the observation
            observation: What was observed
            location: Where the observation took place
            
        Returns:
            Created memory
        """
        # Score importance using LLM
        importance = await self._score_memory_importance(agent, observation)
        
        # Create memory
        memory = Memory(
            agent_id=agent.id,
            content=observation,
            memory_type=MemoryType.PERCEPTION,
            importance_score=importance,
            location=location
        )
        
        # Store memory
        await self._store_memory(memory)
        
        logger.debug(f"Formed perception memory for {agent.name}: {observation[:50]}... (importance: {importance:.1f})")
        return memory
    
    async def retrieve_relevant_memories(
        self,
        agent_id: str,
        context: str,
        limit: int = 5
    ) -> List[MemorySearchResult]:
        """Retrieve memories relevant to the current context.
        
        Args:
            agent_id: ID of the agent
            context: Current context for semantic search
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of relevant memories with scores
        """
        logger.info(f"🔍 COGNITIVE PROCESS: Retrieving relevant memories for {agent_id} - query: '{context[:50]}...'")
        
        try:
            # Generate embedding for the context query
            embedding_response = await self.llm_service.ollama_client.embeddings(
                model=self.llm_service.settings.ollama_embedding_model,
                prompt=context
            )
            
            # Search vector store for similar memories
            vector_results = await self.vector_store.search_memories(
                query_embedding=embedding_response.embedding,
                agent_id=agent_id,
                limit=limit * 2  # Get more candidates for reranking
            )
            
            # Get full memory objects from SQLite
            enhanced_results = []
            for memory_id, semantic_score in vector_results:
                try:
                    # Get full memory from SQLite
                    memory = await self.sqlite_store.get_memory(memory_id)
                    if not memory:
                        continue
                    
                    # Calculate time decay (more recent = higher score)
                    hours_ago = (datetime.utcnow() - memory.timestamp).total_seconds() / 3600
                    recency_score = self._calculate_time_decay(hours_ago)
                    
                    # Normalize importance (0-10 -> 0-1)
                    importance_score = memory.importance_score / 10.0
                    
                    # Calculate final hybrid score with default weights
                    final_score = (
                        0.6 * semantic_score +
                        0.2 * recency_score +
                        0.2 * importance_score
                    )
                    
                    enhanced_result = MemorySearchResult(
                        memory=memory,
                        score=final_score,
                        semantic_score=semantic_score,
                        recency_score=recency_score,
                        importance_score=importance_score
                    )
                    enhanced_results.append(enhanced_result)
                    
                except Exception as e:
                    logger.warning(f"Failed to retrieve memory {memory_id}: {e}")
                    continue
            
            # Sort by final score and return
            enhanced_results.sort(key=lambda x: x.score, reverse=True)
            final_results = enhanced_results[:limit]
            
            logger.info(f"🎯 MEMORY RETRIEVAL: Found {len(final_results)} relevant memories for {agent_id}")
            return final_results
            
        except Exception as e:
            logger.error(f"Failed to retrieve memories for {agent_id}: {e}")
            return []
    
    async def get_recent_memories(
        self,
        agent_id: str,
        limit: int = 10,
        hours: int = 24
    ) -> List[Memory]:
        """Get recent memories for an agent.
        
        Args:
            agent_id: ID of the agent
            limit: Maximum number of memories
            hours: How many hours back to look
            
        Returns:
            List of recent memories
        """
        try:
            return await self.sqlite_store.get_recent_memories(
                agent_id=agent_id,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Failed to get recent memories for {agent_id}: {e}")
            return []
    
    def _create_action_memory_content(
        self,
        agent: Agent,
        action: Action,
        result: ActionResult,
        location: str
    ) -> str:
        """Create memory content from action and result.
        
        Args:
            agent: The agent
            action: The action performed
            result: Action result
            location: Location where action happened
            
        Returns:
            Memory content string
        """
        action_type = action.action_type.value if hasattr(action.action_type, 'value') else str(action.action_type)
        
        if action_type == "move":
            previous_location = result.side_effects.get("previous_location", "unknown")
            new_location = result.side_effects.get("new_location", location)
            return f"I moved from {previous_location} to {new_location}. {result.message}"
        
        elif action_type == "wait":
            duration = result.side_effects.get("duration_minutes", 5)
            reason = action.parameters.get("reason", "")
            if reason:
                return f"I waited for {duration} minutes at {location} because {reason}."
            else:
                return f"I waited for {duration} minutes at {location}."
        
        elif action_type == "observe":
            return f"I observed my surroundings at {location}. {result.message}"
        
        elif action_type == "interact":
            interaction_type = action.parameters.get("interaction_type", "interaction")
            target = action.parameters.get("target_object_id") or action.parameters.get("target_agent_id")
            if target:
                return f"I {interaction_type} with {target} at {location}. {result.message}"
            else:
                return f"I {interaction_type} at {location}. {result.message}"
        
        else:
            return f"I performed {action_type} at {location}. {result.message}"
    
    async def _score_memory_importance(self, agent: Agent, content: str) -> float:
        """Score the importance of a memory using LLM.
        
        Args:
            agent: The agent
            content: Memory content
            
        Returns:
            Importance score (0-10)
        """
        logger.info(f"📊 COGNITIVE PROCESS: Scoring memory importance for {agent.name} - '{content[:50]}...'")
        
        try:
            # Build prompt for importance scoring
            prompt = f"""Rate the importance of this memory for {agent.name}.

Agent background: {agent.bio}
Agent personality: {agent.personality}

Memory: "{content}"

Rate from 0-10 where:
- 0-2: Mundane, routine activities (walking, waiting briefly)
- 3-4: Normal daily activities (basic interactions, simple observations)
- 5-6: Meaningful activities (social interactions, goal progress)
- 7-8: Important events (conflicts, significant achievements, emotional moments)
- 9-10: Life-changing events (major decisions, intense experiences)

Consider the agent's personality and background. What would be important to this specific person?

Respond with just a number from 0-10."""

            response = await self.llm_service.ollama_client.generate(
                model=self.llm_service.settings.ollama_model,
                prompt=prompt,
                options={
                    "temperature": 0.3,  # Lower temperature for consistent scoring
                    "num_predict": 10
                }
            )
            
            # Extract number from response
            import re
            numbers = re.findall(r'\d+\.?\d*', response.response)
            if numbers:
                score = float(numbers[0])
                final_score = max(0.0, min(10.0, score))  # Clamp to 0-10
                logger.info(f"📈 IMPORTANCE SCORED: {agent.name} memory = {final_score:.1f}/10")
                return final_score
            else:
                logger.warning(f"Could not parse importance score from LLM response: {response.response}")
                logger.info(f"📈 IMPORTANCE SCORED: {agent.name} memory = 3.0/10 (default)")
                return 3.0  # Default to moderate importance
                
        except Exception as e:
            logger.error(f"Failed to score memory importance: {e}")
            return 3.0  # Default fallback
    
    def _calculate_time_decay(self, hours_ago: float) -> float:
        """Calculate recency score using exponential decay.
        
        Args:
            hours_ago: How many hours ago the memory was formed
            
        Returns:
            Recency score (0-1, with 1 being most recent)
        """
        # Exponential decay with 24-hour half-life
        half_life_hours = 24.0
        return math.exp(-hours_ago * math.log(2) / half_life_hours)
    
    async def _store_memory_embedding(self, memory: Memory) -> None:
        """Generate embedding and store in vector database.
        
        Args:
            memory: Memory to store
        """
        logger.info(f"🔤 COGNITIVE PROCESS: Generating embedding for {memory.agent_id} memory - '{memory.content[:50]}...'")
        
        try:
            # Generate embedding using LLM service
            embedding_response = await self.llm_service.ollama_client.embeddings(
                model=self.llm_service.settings.ollama_embedding_model,
                prompt=memory.content
            )
            
            # Store in vector database
            embedding_id = await self.vector_store.add_memory_embedding(memory, embedding_response.embedding)
            
            # Update memory with embedding reference
            memory.embedding_id = embedding_id
            
            logger.info(f"💾 EMBEDDING STORED: {memory.agent_id} memory embedded and indexed")
            
        except Exception as e:
            logger.error(f"Failed to generate/store embedding for memory {memory.id}: {e}")
            # Don't raise - memory can exist without embedding
    
    async def _store_memory(self, memory: Memory) -> None:
        """Store memory in both SQLite and vector database.
        
        Args:
            memory: Memory to store
        """
        try:
            # Store in SQLite
            await self.sqlite_store.add_memory(memory)
            
            # Generate embedding and store in vector database
            await self._store_memory_embedding(memory)
            
        except Exception as e:
            logger.error(f"Failed to store memory {memory.id}: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if memory system is working.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Test SQLite connection
            await self.sqlite_store.connect()
            
            # Test vector store
            self.vector_store.initialize_collections()
            
            # Test LLM service
            llm_healthy = await self.llm_service.health_check()
            
            return llm_healthy
            
        except Exception as e:
            logger.warning(f"Memory system health check failed: {e}")
            return False
