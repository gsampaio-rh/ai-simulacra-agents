"""Vector storage implementation using Chroma for semantic search."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from uuid import UUID

import chromadb
from chromadb.config import Settings

from ..models.memory import Memory, MemorySearchResult

logger = logging.getLogger(__name__)


class VectorStore:
    """Chroma-based vector storage for semantic similarity search."""
    
    def __init__(self, persist_directory: str = "data/chroma"):
        """Initialize vector store.
        
        Args:
            persist_directory: Directory to persist Chroma data
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize Chroma client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                allow_reset=True,
                anonymized_telemetry=False
            )
        )
        
        # Collections for different types of content
        self.memory_collection = None
        self.reflection_collection = None
    
    def initialize_collections(self) -> None:
        """Initialize Chroma collections."""
        try:
            # Memory collection for agent memories
            self.memory_collection = self.client.get_or_create_collection(
                name="agent_memories",
                metadata={"description": "Agent memory embeddings for semantic search"}
            )
            
            # Reflection collection for high-level insights
            self.reflection_collection = self.client.get_or_create_collection(
                name="agent_reflections", 
                metadata={"description": "Agent reflection embeddings"}
            )
            
            logger.info("Initialized Chroma collections")
            
        except Exception as e:
            logger.error(f"Failed to initialize collections: {e}")
            raise
    
    async def add_memory_embedding(
        self,
        memory: Memory,
        embedding: List[float]
    ) -> str:
        """Add a memory embedding to the vector store.
        
        Args:
            memory: The memory object
            embedding: The embedding vector
            
        Returns:
            The embedding ID for reference
        """
        if not self.memory_collection:
            self.initialize_collections()
        
        embedding_id = str(memory.id)
        
        # Prepare metadata
        metadata = {
            "agent_id": memory.agent_id,
            "memory_type": memory.memory_type.value if hasattr(memory.memory_type, 'value') else memory.memory_type,
            "timestamp": memory.timestamp.isoformat(),
            "importance": memory.importance_score,
            "location": memory.location or "",
        }
        
        try:
            self.memory_collection.add(
                embeddings=[embedding],
                documents=[memory.content],
                metadatas=[metadata],
                ids=[embedding_id]
            )
            
            logger.debug(f"Added embedding for memory {embedding_id}")
            return embedding_id
            
        except Exception as e:
            logger.error(f"Failed to add memory embedding: {e}")
            raise
    
    async def search_memories(
        self,
        query_embedding: List[float],
        agent_id: str,
        limit: int = 10,
        memory_types: Optional[List[str]] = None,
        min_importance: Optional[float] = None
    ) -> List[Tuple[str, float]]:
        """Search for similar memories using vector similarity.
        
        Args:
            query_embedding: The query embedding vector
            agent_id: ID of the agent to search memories for
            limit: Maximum number of results
            memory_types: Optional filter by memory types
            min_importance: Optional minimum importance threshold
            
        Returns:
            List of (memory_id, similarity_score) tuples
        """
        if not self.memory_collection:
            self.initialize_collections()
        
        # Build where clause for filtering
        where_clause = {"agent_id": agent_id}
        
        if memory_types:
            where_clause["memory_type"] = {"$in": memory_types}
        
        if min_importance is not None:
            where_clause["importance"] = {"$gte": min_importance}
        
        try:
            results = self.memory_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_clause,
                include=["distances", "metadatas"]
            )
            
            # Extract results
            memory_similarities = []
            if results["ids"]:
                for memory_id, distance in zip(results["ids"][0], results["distances"][0]):
                    # Convert distance to similarity (Chroma uses cosine distance)
                    # Clamp distance to reasonable range and convert to 0-1 similarity
                    clamped_distance = max(0.0, min(2.0, distance))  # Cosine distance is typically 0-2
                    similarity = 1.0 - (clamped_distance / 2.0)  # Convert to 0-1 similarity
                    memory_similarities.append((memory_id, similarity))
            
            logger.debug(f"Found {len(memory_similarities)} similar memories for agent {agent_id}")
            return memory_similarities
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []
    
    async def add_reflection_embedding(
        self,
        reflection_id: UUID,
        agent_id: str,
        content: str,
        embedding: List[float],
        supporting_memories: List[UUID]
    ) -> str:
        """Add a reflection embedding to the vector store.
        
        Args:
            reflection_id: UUID of the reflection
            agent_id: ID of the agent
            content: Reflection content
            embedding: The embedding vector
            supporting_memories: UUIDs of supporting memories
            
        Returns:
            The embedding ID for reference
        """
        if not self.reflection_collection:
            self.initialize_collections()
        
        embedding_id = str(reflection_id)
        
        # Prepare metadata
        metadata = {
            "agent_id": agent_id,
            "supporting_memories": ",".join(str(m) for m in supporting_memories),
            "timestamp": str(reflection_id)  # Using UUID as timestamp reference
        }
        
        try:
            self.reflection_collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata],
                ids=[embedding_id]
            )
            
            logger.debug(f"Added reflection embedding {embedding_id}")
            return embedding_id
            
        except Exception as e:
            logger.error(f"Failed to add reflection embedding: {e}")
            raise
    
    async def search_reflections(
        self,
        query_embedding: List[float],
        agent_id: str,
        limit: int = 5
    ) -> List[Tuple[str, float]]:
        """Search for similar reflections.
        
        Args:
            query_embedding: The query embedding vector
            agent_id: ID of the agent to search reflections for
            limit: Maximum number of results
            
        Returns:
            List of (reflection_id, similarity_score) tuples
        """
        if not self.reflection_collection:
            self.initialize_collections()
        
        try:
            results = self.reflection_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where={"agent_id": agent_id},
                include=["distances"]
            )
            
            # Extract results
            reflection_similarities = []
            if results["ids"]:
                for reflection_id, distance in zip(results["ids"][0], results["distances"][0]):
                    similarity = 1.0 - distance
                    reflection_similarities.append((reflection_id, similarity))
            
            return reflection_similarities
            
        except Exception as e:
            logger.error(f"Failed to search reflections: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, int]:
        """Get statistics about the collections."""
        stats = {}
        
        if self.memory_collection:
            stats["memory_count"] = self.memory_collection.count()
        
        if self.reflection_collection:
            stats["reflection_count"] = self.reflection_collection.count()
        
        return stats
    
    def reset_collections(self) -> None:
        """Reset all collections (useful for testing)."""
        try:
            if self.memory_collection:
                self.client.delete_collection("agent_memories")
            
            if self.reflection_collection:
                self.client.delete_collection("agent_reflections")
            
            # Reinitialize
            self.initialize_collections()
            logger.info("Reset all collections")
            
        except Exception as e:
            logger.error(f"Failed to reset collections: {e}")
            raise
