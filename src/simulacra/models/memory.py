"""Memory-related data models."""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MemoryType(Enum):
    """Types of memories that can be stored."""
    
    PERCEPTION = "perception"  # Something the agent observed
    ACTION = "action"         # Something the agent did
    REFLECTION = "reflection" # A synthesized insight
    DIALOGUE = "dialogue"     # Conversation content
    PLAN = "plan"            # Planning-related memory


class Memory(BaseModel):
    """A single memory entry in an agent's memory stream."""
    
    id: UUID = Field(default_factory=uuid4)
    agent_id: str = Field(..., description="ID of the agent who owns this memory")
    content: str = Field(..., description="The actual memory content")
    memory_type: MemoryType = Field(default=MemoryType.PERCEPTION)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    importance_score: float = Field(
        default=0.0, 
        ge=0.0, 
        le=10.0,
        description="Importance score from 0-10"
    )
    embedding_id: Optional[str] = Field(
        default=None,
        description="Reference to the embedding in the vector database"
    )
    location: Optional[str] = Field(
        default=None,
        description="Location where this memory was formed"
    )
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class Reflection(BaseModel):
    """A high-level reflection synthesized from multiple memories."""
    
    id: UUID = Field(default_factory=uuid4)
    agent_id: str = Field(..., description="ID of the agent who made this reflection")
    content: str = Field(..., description="The reflection insight")
    supporting_memories: List[UUID] = Field(
        default_factory=list,
        description="Memory IDs that support this reflection"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    importance_score: float = Field(
        default=5.0,
        ge=0.0,
        le=10.0,
        description="Reflections typically have higher importance"
    )
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class RetrievalWeights(BaseModel):
    """Weights for the hybrid retrieval scoring formula."""
    
    semantic: float = Field(default=0.6, ge=0.0, le=1.0)
    recency: float = Field(default=0.2, ge=0.0, le=1.0)
    importance: float = Field(default=0.2, ge=0.0, le=1.0)
    
    def __post_init__(self) -> None:
        """Ensure weights sum to 1.0."""
        total = self.semantic + self.recency + self.importance
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Weights must sum to 1.0, got {total}")


class MemoryQuery(BaseModel):
    """Query parameters for memory retrieval."""
    
    agent_id: str = Field(..., description="ID of the agent to query")
    query_text: str = Field(..., description="The query text for semantic search")
    limit: int = Field(default=10, ge=1, le=100)
    memory_types: Optional[List[MemoryType]] = Field(
        default=None,
        description="Filter by memory types"
    )
    min_importance: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=10.0,
        description="Minimum importance score"
    )
    weights: RetrievalWeights = Field(default_factory=RetrievalWeights)


class MemorySearchResult(BaseModel):
    """Result from a memory search operation."""
    
    memory: Memory
    score: float = Field(..., description="Combined retrieval score")
    semantic_score: float = Field(..., description="Semantic similarity score")
    recency_score: float = Field(..., description="Recency score")
    importance_score: float = Field(..., description="Normalized importance score")
