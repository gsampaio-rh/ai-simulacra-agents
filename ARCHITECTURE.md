# System Architecture

This document describes the technical architecture of the AI Simulacra Agents system, detailing component relationships, data flows, and design decisions.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Component Details](#component-details)
- [Data Flow](#data-flow)
- [Storage Architecture](#storage-architecture)
- [API Design](#api-design)
- [Performance Considerations](#performance-considerations)
- [Security & Privacy](#security--privacy)
- [Scalability](#scalability)

## Architecture Overview

The system follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Interface                        │
│                   (Terminal Commands)                   │
├─────────────────────────────────────────────────────────┤
│                   FastAPI Service                       │
│              (Orchestration & REST API)                │
├─────────────────────────────────────────────────────────┤
│                  Simulation Layer                       │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│   │ Time Manager│ │ World State │ │ Event Bus   │      │
│   └─────────────┘ └─────────────┘ └─────────────┘      │
├─────────────────────────────────────────────────────────┤
│                    Agent Layer                          │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│   │   Memory    │ │  Retrieval  │ │ Reflection  │      │
│   │   Stream    │ │   Engine    │ │   Engine    │      │
│   └─────────────┘ └─────────────┘ └─────────────┘      │
│   ┌─────────────┐ ┌─────────────┐                       │
│   │  Planning   │ │   Action    │                       │
│   │   Engine    │ │   Engine    │                       │
│   └─────────────┘ └─────────────┘                       │
├─────────────────────────────────────────────────────────┤
│                Infrastructure Layer                     │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│   │   SQLite    │ │   Chroma    │ │   Ollama    │      │
│   │  (Metadata) │ │ (Vectors)   │ │ (LLM/Embed) │      │
│   └─────────────┘ └─────────────┘ └─────────────┘      │
└─────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Infrastructure Layer

#### SQLite Database
**Purpose**: Persistent storage for structured data

**Schema Design**:
```sql
-- Core entities
CREATE TABLE agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    bio TEXT,
    home_location TEXT,
    personality TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    importance_score REAL DEFAULT 0.0,
    memory_type TEXT DEFAULT 'perception', -- perception, action, reflection
    embedding_id TEXT, -- Reference to Chroma
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);

CREATE TABLE reflections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    content TEXT NOT NULL,
    supporting_memories TEXT, -- JSON array of memory IDs
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);

CREATE TABLE plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    plan_type TEXT NOT NULL, -- daily, hourly, task
    content TEXT NOT NULL, -- JSON plan structure
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status TEXT DEFAULT 'active', -- active, completed, cancelled
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);

CREATE TABLE world_state (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL, -- place, object, agent_location
    data TEXT NOT NULL, -- JSON data
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_type TEXT NOT NULL,
    agent_id TEXT,
    location TEXT,
    content TEXT NOT NULL,
    observers TEXT -- JSON array of agent IDs who can perceive this
);
```

#### Chroma Vector Database
**Purpose**: Semantic similarity search for memory retrieval

**Collections**:
- `agent_memories`: Embeddings of all agent memories
- `reflections`: Embeddings of reflection summaries

**Metadata Schema**:
```python
{
    "agent_id": str,
    "timestamp": float,
    "importance": float,
    "memory_type": str,
    "sqlite_id": int
}
```

#### Ollama Integration
**Purpose**: Local LLM inference and embedding generation

**Required Models**:
- **LLM**: `llama3.2:3b` or `mistral:7b` for text generation
- **Embeddings**: `nomic-embed-text` for vector generation

**Usage Patterns**:
- Synchronous calls for reflection and planning
- Async batching for embedding generation
- Connection pooling for concurrent requests

### 2. Agent Layer

#### Memory Stream
**Responsibilities**:
- Store every perception, action, and reflection
- Assign importance scores using LLM evaluation
- Generate embeddings for semantic search

**Interface**:
```python
class MemoryStream:
    async def add_memory(
        self, 
        agent_id: str, 
        content: str, 
        memory_type: MemoryType = MemoryType.PERCEPTION,
        importance: Optional[float] = None
    ) -> Memory
    
    async def get_recent_memories(
        self, 
        agent_id: str, 
        count: int = 10
    ) -> List[Memory]
    
    async def search_memories(
        self, 
        agent_id: str, 
        query: str, 
        limit: int = 10
    ) -> List[Memory]
```

#### Retrieval Engine
**Responsibilities**:
- Hybrid scoring combining semantic, recency, and importance
- Configurable weight parameters
- Context-aware memory selection

**Scoring Formula**:
```python
def calculate_retrieval_score(
    semantic_sim: float,  # 0-1 from cosine similarity
    recency: float,       # 0-1 from time decay function
    importance: float,    # 0-10 normalized to 0-1
    weights: RetrievalWeights = RetrievalWeights()
) -> float:
    return (
        weights.semantic * semantic_sim +
        weights.recency * recency +
        weights.importance * importance
    )
```

**Time Decay Function**:
```python
def time_decay(hours_ago: float) -> float:
    """Exponential decay with configurable half-life"""
    return math.exp(-hours_ago / DECAY_HALF_LIFE)
```

#### Reflection Engine
**Responsibilities**:
- Monitor cumulative memory importance
- Generate high-level insights using LLM
- Create reflection memories with citations

**Reflection Trigger**:
```python
class ReflectionTrigger:
    threshold: float = 30.0  # Cumulative importance threshold
    
    def should_reflect(self, agent_id: str) -> bool:
        recent_importance = sum(
            memory.importance 
            for memory in get_recent_memories(agent_id)
            if not memory.is_reflection
        )
        return recent_importance >= self.threshold
```

**Reflection Process**:
1. Retrieve high-importance recent memories
2. Generate 3-5 key insights using LLM
3. Store reflections with memory citations
4. Reset importance accumulator

#### Planning Engine
**Responsibilities**:
- Generate hierarchical plans (day → hour → task)
- Update plans based on world changes
- Execute plan decomposition

**Plan Schema**:
```python
@dataclass
class DailyPlan:
    date: datetime.date
    goals: List[str]
    hourly_blocks: List[HourlyBlock]

@dataclass
class HourlyBlock:
    start_time: datetime.time
    duration_minutes: int
    activity: str
    location: Optional[str]
    tasks: List[Task]

@dataclass
class Task:
    description: str
    duration_minutes: int
    action_type: ActionType
    parameters: Dict[str, Any]
```

#### Action Engine
**Responsibilities**:
- Execute agent decisions in world state
- Generate observable events
- Handle action validation and side effects

**Supported Actions**:
```python
class ActionType(Enum):
    MOVE = "move"
    SAY = "say" 
    INTERACT = "interact"
    WAIT = "wait"
    REFLECT = "reflect"
```

### 3. Simulation Layer

#### Time Manager
**Responsibilities**:
- Discrete time progression (5-minute ticks)
- Simulation control (start/pause/step)
- Schedule coordination

**Interface**:
```python
class TimeManager:
    current_tick: int = 0
    tick_duration_minutes: int = 5
    is_running: bool = False
    
    async def start_simulation(self) -> None
    async def pause_simulation(self) -> None
    async def advance_tick(self) -> None
    async def fast_forward(self, ticks: int) -> None
```

#### World State
**Responsibilities**:
- Maintain places, objects, and agent locations
- Handle spatial relationships
- Validate action preconditions

**State Representation**:
```python
@dataclass
class WorldState:
    places: Dict[str, Place]
    objects: Dict[str, WorldObject]
    agent_locations: Dict[str, str]  # agent_id -> place_id
    
    def can_perceive(self, observer: str, event: Event) -> bool:
        """Check if agent can perceive an event based on location"""
        observer_location = self.agent_locations.get(observer)
        return observer_location == event.location
```

#### Event Bus
**Responsibilities**:
- Propagate events to relevant agents
- Generate perceptions for memory system
- Handle event ordering and causality

**Event Flow**:
1. Action execution generates events
2. Event bus determines observers
3. Perceptions created for each observer
4. Memories added to relevant agents

### 4. API Layer

#### FastAPI Service
**Responsibilities**:
- REST API for simulation control
- Agent inspection endpoints
- Memory query interface

**Key Endpoints**:
```python
# Simulation control
POST /simulation/start
POST /simulation/pause
POST /simulation/step
GET  /simulation/status

# Agent management
GET  /agents
GET  /agents/{agent_id}
GET  /agents/{agent_id}/memories
POST /agents/{agent_id}/reflect

# Memory operations
POST /memory/add
GET  /memory/query
GET  /memory/recent
```

## Data Flow

### 1. Memory Formation Flow
```
Action/Perception → Importance Scoring → Embedding Generation → 
SQLite Storage → Chroma Indexing → Reflection Trigger Check
```

### 2. Decision Making Flow
```
Current Context → Memory Retrieval → Plan Consultation → 
Action Selection → World State Update → Event Generation
```

### 3. Simulation Tick Flow
```
Tick Start → For Each Agent:
  - Retrieve Relevant Memories
  - Check Reflection Trigger
  - Update/Generate Plans
  - Select Next Action
  - Execute Action
  - Generate Events
  - Create Perceptions
→ Tick Complete
```

## Performance Considerations

### Database Optimization
- **SQLite WAL Mode**: Concurrent reads during writes
- **Memory Indexing**: Compound indexes on (agent_id, timestamp)
- **Prepared Statements**: Reuse query compilation
- **Connection Pooling**: Limit concurrent connections

### Vector Search Optimization
- **Batch Embeddings**: Generate embeddings in batches
- **Index Parameters**: Tune HNSW parameters for recall/speed
- **Memory Limits**: Configure collection size limits
- **Similarity Thresholds**: Filter low-similarity results

### LLM Optimization
- **Model Selection**: Balance capability vs. speed
- **Context Length**: Optimize prompt templates
- **Caching**: Cache LLM responses for repeated queries
- **Async Processing**: Non-blocking LLM calls

### Memory Management
- **Memory Archival**: Archive old memories to reduce active set
- **Reflection Caching**: Cache reflection results
- **Plan Memoization**: Reuse plan components when possible

## Security & Privacy

### Data Protection
- **Local Storage**: All data remains on user machine
- **No Cloud Deps**: No external API calls except local Ollama
- **Encryption**: Optional SQLite encryption for sensitive data

### Input Validation
- **Schema Validation**: Pydantic models for all inputs
- **SQL Injection**: Parameterized queries only
- **Path Traversal**: Validate file paths for config loading

### Resource Limits
- **Rate Limiting**: Prevent excessive LLM calls
- **Memory Limits**: Cap memory usage per agent
- **Disk Space**: Monitor storage growth

## Scalability

### Current Limitations
- **Single Machine**: No distributed processing
- **SQLite Limits**: ~1TB practical limit
- **Chroma Scaling**: Memory-bound vector storage

### Future Scaling Options
- **Database Sharding**: Partition by agent_id
- **Vector DB Alternatives**: Consider FAISS for larger datasets
- **Distributed Simulation**: Agent-per-process architecture
- **Streaming Events**: Event sourcing for large simulations

### Performance Targets
- **Agent Count**: Support 10-50 agents simultaneously
- **Memory Operations**: <100ms for memory retrieval
- **Reflection Generation**: <5s for reflection synthesis
- **Tick Processing**: <1s per simulation tick

## Technology Decisions

### Why SQLite?
- **Zero Configuration**: No database server required
- **ACID Compliance**: Reliable transactions
- **Performance**: Excellent for read-heavy workloads
- **Portability**: Single file database

### Why Chroma?
- **Local First**: No cloud dependencies
- **Python Native**: Seamless integration
- **Metadata Support**: Rich filtering capabilities
- **Active Development**: Regular updates and improvements

### Why FastAPI?
- **Modern Python**: Async/await support
- **Type Safety**: Pydantic integration
- **Documentation**: Auto-generated OpenAPI specs
- **Performance**: Competitive with Node.js

### Why Ollama?
- **Local Inference**: No API keys or network calls
- **Model Management**: Easy model installation
- **Performance**: Optimized for consumer hardware
- **Community**: Strong ecosystem and model selection
