"""Pytest configuration and fixtures for AI Simulacra Agents tests."""

import asyncio
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio

from simulacra.config import Settings
from simulacra.storage import SQLiteStore, VectorStore
from simulacra.models.agent import Agent, AgentState
from simulacra.models.memory import Memory, MemoryType
from simulacra.models.world import Place, WorldObject


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def test_settings(temp_dir: Path) -> Settings:
    """Create test settings with temporary paths."""
    return Settings(
        sqlite_db_path=str(temp_dir / "test.db"),
        chroma_persist_dir=str(temp_dir / "chroma"),
        config_dir=str(temp_dir / "config"),
        debug=True,
        log_level="DEBUG"
    )


@pytest_asyncio.fixture
async def sqlite_store(test_settings: Settings) -> AsyncGenerator[SQLiteStore, None]:
    """Create a test SQLite store."""
    store = SQLiteStore(test_settings.sqlite_db_path)
    await store.initialize_schema()
    yield store
    await store.disconnect()


@pytest.fixture
def vector_store(test_settings: Settings) -> VectorStore:
    """Create a test vector store."""
    store = VectorStore(test_settings.chroma_persist_dir)
    store.initialize_collections()
    # Reset collections for clean state
    store.reset_collections()
    return store


@pytest.fixture
def sample_agent() -> Agent:
    """Create a sample agent for testing."""
    return Agent(
        id="test_agent",
        name="Test Agent",
        bio="A test agent for unit testing",
        personality="helpful, reliable, test-oriented",
        home_location="test_location",
        relationships={"other_agent": "friend"}
    )


@pytest.fixture
def sample_memory(sample_agent: Agent) -> Memory:
    """Create a sample memory for testing."""
    return Memory(
        agent_id=sample_agent.id,
        content="This is a test memory about something important",
        memory_type=MemoryType.PERCEPTION,
        importance_score=5.0,
        location="test_location"
    )


@pytest.fixture
def sample_place() -> Place:
    """Create a sample place for testing."""
    return Place(
        id="test_place",
        name="Test Place", 
        description="A place for testing",
        capacity=10,
        properties={"test": True},
        connected_places=["other_place"]
    )


@pytest.fixture
def sample_object() -> WorldObject:
    """Create a sample world object for testing."""
    return WorldObject(
        id="test_object",
        name="Test Object",
        description="An object for testing",
        location="test_place",
        properties={"interactive": True},
        interactions=["use", "examine"],
        is_movable=True
    )


@pytest.fixture
def sample_embedding() -> list[float]:
    """Create a sample embedding vector for testing."""
    # Create a simple 384-dimensional embedding (typical for small models)
    return [0.1] * 384
