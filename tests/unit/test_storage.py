"""Unit tests for storage layer."""

import pytest
from uuid import uuid4

from simulacra.models.agent import Agent
from simulacra.models.memory import Memory, MemoryType
from simulacra.models.world import Place, WorldObject, AgentLocation
from simulacra.storage import SQLiteStore, VectorStore


class TestSQLiteStore:
    """Test SQLite storage operations."""
    
    @pytest.mark.asyncio
    async def test_create_and_get_agent(self, sqlite_store: SQLiteStore, sample_agent: Agent):
        """Test creating and retrieving an agent."""
        # Create agent
        await sqlite_store.create_agent(sample_agent)
        
        # Retrieve agent
        retrieved_agent = await sqlite_store.get_agent(sample_agent.id)
        
        assert retrieved_agent is not None
        assert retrieved_agent.id == sample_agent.id
        assert retrieved_agent.name == sample_agent.name
        assert retrieved_agent.bio == sample_agent.bio
        assert retrieved_agent.personality == sample_agent.personality
        assert retrieved_agent.home_location == sample_agent.home_location
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_agent(self, sqlite_store: SQLiteStore):
        """Test retrieving a non-existent agent."""
        result = await sqlite_store.get_agent("nonexistent")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_add_and_get_memory(self, sqlite_store: SQLiteStore, sample_memory: Memory):
        """Test adding and retrieving memories."""
        # First create the agent
        from simulacra.models.agent import Agent
        agent = Agent(
            id=sample_memory.agent_id,
            name="Test Agent",
            bio="Test bio", 
            personality="test",
            home_location="test"
        )
        await sqlite_store.create_agent(agent)
        
        # Add memory
        await sqlite_store.add_memory(sample_memory)
        
        # Retrieve memories
        memories = await sqlite_store.get_recent_memories(sample_memory.agent_id, limit=5)
        
        assert len(memories) == 1
        assert memories[0].content == sample_memory.content
        assert memories[0].memory_type == sample_memory.memory_type
        assert memories[0].importance_score == sample_memory.importance_score
    
    @pytest.mark.asyncio
    async def test_create_place(self, sqlite_store: SQLiteStore, sample_place: Place):
        """Test creating a place."""
        await sqlite_store.create_place(sample_place)
        
        # Verify it was created by checking database stats
        stats = await sqlite_store.get_database_stats()
        assert stats["places_count"] == 1
    
    @pytest.mark.asyncio
    async def test_create_object(self, sqlite_store: SQLiteStore, sample_object: WorldObject, sample_place: Place):
        """Test creating a world object."""
        # Create place first (foreign key dependency)
        await sqlite_store.create_place(sample_place)
        
        # Create object
        sample_object.location = sample_place.id
        await sqlite_store.create_object(sample_object)
        
        # Verify it was created
        stats = await sqlite_store.get_database_stats()
        assert stats["objects_count"] == 1
    
    @pytest.mark.asyncio
    async def test_agent_location_tracking(self, sqlite_store: SQLiteStore, sample_agent: Agent, sample_place: Place):
        """Test agent location tracking."""
        # Create dependencies
        await sqlite_store.create_place(sample_place)
        await sqlite_store.create_agent(sample_agent)
        
        # Update location
        location = AgentLocation(
            agent_id=sample_agent.id,
            place_id=sample_place.id
        )
        await sqlite_store.update_agent_location(location)
        
        # Check agents at location
        agents = await sqlite_store.get_agents_at_location(sample_place.id)
        assert sample_agent.id in agents


class TestVectorStore:
    """Test vector storage operations."""
    
    @pytest.mark.asyncio
    async def test_add_memory_embedding(self, vector_store: VectorStore, sample_memory: Memory, sample_embedding: list[float]):
        """Test adding a memory embedding."""
        embedding_id = await vector_store.add_memory_embedding(sample_memory, sample_embedding)
        
        assert embedding_id == str(sample_memory.id)
        
        # Check collection stats
        stats = vector_store.get_collection_stats()
        assert stats["memory_count"] == 1
    
    @pytest.mark.asyncio
    async def test_search_memories(self, vector_store: VectorStore, sample_memory: Memory, sample_embedding: list[float]):
        """Test searching for similar memories."""
        # Add a memory embedding
        await vector_store.add_memory_embedding(sample_memory, sample_embedding)
        
        # Search for similar memories
        results = await vector_store.search_memories(
            query_embedding=sample_embedding,
            agent_id=sample_memory.agent_id,
            limit=5
        )
        
        assert len(results) == 1
        memory_id, similarity = results[0]
        assert memory_id == str(sample_memory.id)
        assert similarity > 0.9  # Should be very similar to itself
    
    @pytest.mark.asyncio
    async def test_search_empty_collection(self, vector_store: VectorStore, sample_embedding: list[float]):
        """Test searching in an empty collection."""
        results = await vector_store.search_memories(
            query_embedding=sample_embedding,
            agent_id="nonexistent_agent",
            limit=5
        )
        
        assert len(results) == 0
    
    def test_collection_initialization(self, vector_store: VectorStore):
        """Test that collections are properly initialized."""
        stats = vector_store.get_collection_stats()
        
        assert "memory_count" in stats
        assert "reflection_count" in stats
        assert stats["memory_count"] == 0
        assert stats["reflection_count"] == 0
