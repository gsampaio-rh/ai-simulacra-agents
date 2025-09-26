# System Architecture

This document describes the technical architecture of the AI Simulacra Agents system as of September 2025, detailing implemented components, data flows, and design decisions. This reflects the current state through M4 (Reflection System) with breakthrough LLM-powered cognitive architecture.

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

The system implements a breakthrough cognitive architecture with real LLM-powered agent thinking. The layered design provides clear separation of concerns while enabling sophisticated AI behavior:

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Interface                        │
│           (Rich Terminal UI + Professional CLI)        │
├─────────────────────────────────────────────────────────┤
│                 Simulation Controller                   │
│              (Agent Orchestration & Control)           │
├─────────────────────────────────────────────────────────┤
│                  Simulation Layer                       │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│   │ Time Manager│ │ World State │ │LLM Behavior │      │
│   │(Tick System)│ │(Places/Locs)│ │(Real AI!)   │      │
│   └─────────────┘ └─────────────┘ └─────────────┘      │
├─────────────────────────────────────────────────────────┤
│                Cognitive Agent Layer ✨                │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│   │   Memory    │ │  Retrieval  │ │ Reflection  │      │
│   │   Manager   │ │   Engine    │ │   Engine    │      │
│   │  ✅ IMPL    │ │  ✅ IMPL    │ │  ✅ IMPL    │      │
│   └─────────────┘ └─────────────┘ └─────────────┘      │
│   ┌─────────────┐ ┌─────────────┐                       │
│   │  Planning   │ │ LLM Service │                       │
│   │   Engine    │ │ ✅ IMPL     │                       │
│   │  🚧 M5      │ │(Embeddings) │                       │
│   └─────────────┘ └─────────────┘                       │
├─────────────────────────────────────────────────────────┤
│                Infrastructure Layer                     │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│   │   SQLite    │ │   Chroma    │ │   Ollama    │      │
│   │ (Structured)│ │ (Vectors)   │ │ (Local LLM) │      │
│   │  ✅ IMPL    │ │  ✅ IMPL    │ │  ✅ IMPL    │      │
│   └─────────────┘ └─────────────┘ └─────────────┘      │
└─────────────────────────────────────────────────────────┘
```

### 🚀 Key Architectural Achievements

**✅ Real LLM Cognition**: Replaced 300+ lines of hard-coded rules with authentic AI reasoning  
**✅ Complete Memory System**: Episodic memory with semantic retrieval and automatic reflection  
**✅ Cognitive Transparency**: Full visibility into agent thinking via emoji-coded logging  
**✅ Beautiful UX**: Rich terminal interface showing agent cognition in real-time

## 🧠 Cognitive Architecture Breakthrough

### The Problem We Solved

Traditional agent simulations use hard-coded behavior rules:
```python
# OLD WAY: Hard-coded personality rules ❌
if agent.personality == "social":
    return "I want to talk to someone"
elif agent.energy < 50:
    return "I should rest"
```

This produces predictable, robotic behavior that doesn't feel authentic.

### Our Solution: Real LLM Cognition

We achieved a breakthrough by giving agents **genuine AI reasoning**:

```python
# NEW WAY: LLM-powered decision making ✅
class LLMBehavior:
    async def choose_action_with_reasoning(self, agent: Agent) -> Tuple[Action, str]:
        # Build rich context with memories and current state
        context = await self._build_agent_context(agent)
        
        # Use LLM for authentic reasoning
        prompt = f"""You are {agent.name}, a character in a social simulation.
        
        Your background: {agent.bio}
        Your personality: {agent.personality}
        Current situation: {context}
        
        Think about what you want to do and why, then choose an action."""
        
        response = await self.llm_service.generate_text(prompt)
        action, reasoning = self._parse_llm_response(response)
        return action, reasoning
```

### Result: Authentic Agent Cognition

**Real Agent Reasoning Example**:
```
"I'm feeling a bit down today, my mood is only 5.0 out of 10, and I think it's 
because I haven't had much social interaction lately. As the owner of the cafe, 
I spend most of my time alone preparing food or dealing with administrative tasks. 
I miss the energy and conversation that comes with a bustling community space. 
Maybe I should go to the Community Garden where I might encounter some neighbors."
```

This reasoning is **generated in real-time** by the LLM, not pre-written templates.

### Memory-Influenced Decision Making

Agents don't just think—they **remember and learn**:

1. **Memory Formation**: Every action creates memories with LLM-scored importance
2. **Contextual Retrieval**: Past experiences inform current decisions  
3. **Reflection Integration**: Self-generated insights influence future behavior

**Example of Memory-Influenced Reasoning**:
```
"Based on my recent reflection that 'I crave community connections to fuel my 
creative energy,' and remembering yesterday's satisfying conversation with Maria 
at the garden, I think I should seek out more social interactions today."
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

### 2. Cognitive Agent Layer ✨ IMPLEMENTED

#### Memory Manager
**Status**: ✅ **FULLY IMPLEMENTED** - Episodic memory with semantic retrieval

**Responsibilities**:
- Store every perception, action, and reflection with automatic importance scoring
- Generate embeddings using Ollama for semantic search
- Provide hybrid retrieval (semantic + recency + importance)
- Integration with LLM decision-making process

**Implemented Interface**:
```python
class MemoryManager:
    async def create_memory(
        self, 
        agent_id: str, 
        content: str, 
        memory_type: MemoryType = MemoryType.ACTION,
        importance_score: Optional[float] = None
    ) -> Memory
    
    async def get_recent_memories(
        self, 
        agent_id: str, 
        limit: int = 10
    ) -> List[Memory]
    
    async def search_memories(
        self, 
        agent_id: str, 
        query: str, 
        limit: int = 5
    ) -> List[Memory]
    
    async def get_memories_for_context(
        self,
        agent_id: str,
        current_context: str,
        limit: int = 5
    ) -> List[Memory]
```

**Key Achievement**: Memory system seamlessly integrates with LLM decision-making, providing relevant past experiences as context for authentic reasoning.

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
**Status**: ✅ **FULLY IMPLEMENTED** - Automatic self-awareness generation

**Responsibilities**:
- Monitor cumulative memory importance for automatic triggering
- Generate sophisticated insights using LLM pattern recognition
- Create reflection memories with supporting memory citations
- Beautiful terminal UI for reflection visualization

**Implemented Reflection Trigger**:
```python
class ReflectionEngine:
    def __init__(self, importance_threshold: float = 15.0):
        self.importance_threshold = importance_threshold
    
    async def should_reflect(self, agent_id: str) -> bool:
        """Check if agent has accumulated enough experience to reflect"""
        recent_memories = await self.memory_manager.get_recent_memories(agent_id, 20)
        
        # Calculate importance since last reflection
        cumulative_importance = sum(
            memory.importance_score 
            for memory in recent_memories 
            if memory.memory_type != MemoryType.REFLECTION
        )
        
        return cumulative_importance >= self.importance_threshold
```

**Implemented Reflection Process**:
1. **Automatic Triggering**: Monitor importance accumulation (threshold: 15.0)
2. **Memory Analysis**: Retrieve high-importance recent memories for pattern analysis
3. **LLM Insight Generation**: Generate 3-5 sophisticated behavioral insights
4. **Citation Storage**: Store reflections as high-importance memories (8.0) with supporting evidence
5. **UI Integration**: Beautiful cyan-themed reflection panels in terminal

**Real Reflection Examples**:
- *"Isabella is craving a sense of community and stability after transitioning between spaces"*
- *"Isabella's creative energy is fueled by her interactions with people and environments"*
- *"Isabella is learning to appreciate the value of downtime and reflection"*

#### Planning Engine
**Status**: 🚧 **IN DEVELOPMENT** - M5 Milestone (Next Priority)

**Planned Responsibilities**:
- Generate hierarchical plans based on agent personality and reflections
- LLM-powered goal setting and daily/hourly planning
- Integration with memory and reflection systems for plan adaptation

**Target Implementation**:
```python
class PlanningEngine:
    async def generate_daily_plan(self, agent: Agent) -> DailyPlan:
        """Generate goal-oriented daily plan using LLM and agent context"""
        context = await self._build_planning_context(agent)
        plan = await self.llm_service.generate_plan(agent, context)
        return self._parse_daily_plan(plan)
```

#### LLM Behavior System
**Status**: ✅ **FULLY IMPLEMENTED** - Core breakthrough achievement

**Responsibilities**:
- Real-time LLM-powered decision making (replaced all hard-coded rules)
- Context-aware action selection with authentic reasoning
- Memory-informed decision making
- Integration with simulation controller

**Implemented Actions**:
```python
class ActionType(Enum):
    MOVE = "move"      # ✅ Change agent location
    WAIT = "wait"      # ✅ Stay in place, rest/think
    OBSERVE = "observe" # ✅ Look around current location
    INTERACT = "interact" # ✅ Interact with objects/environment
```

**Key Achievement**: Agents now demonstrate **authentic, unpredictable cognition** using real AI reasoning instead of predetermined responses.

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
