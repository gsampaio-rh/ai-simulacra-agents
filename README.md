# AI Simulacra Agents

A sophisticated AI agent simulation system where autonomous agents think, remember, reflect, and act in a shared world. Built with real LLM-powered cognition for authentic, emergent behavior. No cloud dependencies—runs entirely locally.

## 🚀 Current Status: Advanced Cognitive Agents

**What We've Built**: A complete cognitive agent system with breakthrough features:

- 🧠 **Real LLM-Powered Thinking**: Agents use actual AI reasoning, not hard-coded rules
- 💾 **Episodic Memory System**: Agents remember all experiences with semantic retrieval
- ✨ **Automatic Reflection**: Agents gain self-awareness and insights from their experiences
- 🎨 **Beautiful Terminal UI**: Watch agents think, decide, and reflect in real-time
- 📊 **Research-Grade Export**: Complete cognitive process data for analysis

**Breakthrough Achievement**: Our agents demonstrate genuine cognitive behavior—they think, remember past experiences, reflect on patterns, and make contextual decisions that can surprise even their creators.

## 🎯 What Makes This Special

### Authentic AI Cognition
Unlike rule-based simulations, our agents use **real LLM reasoning**:
```
❌ Old Way: if personality == "social": return "talk to someone"  
✅ Our Way: "I'm feeling a bit down today (mood: 5.0) and I think it's because I haven't had much social interaction lately. As the cafe owner, I spend most of my time alone..."
```

### Complete Cognitive Transparency
Watch every step of the AI's thinking process:
```bash
🧠 Isabella Rodriguez is thinking...
💭 "I'm feeling isolated after yesterday's quiet morning at the cafe. I should reach out to the community..."
✨ Decision: move to Community Garden
🎯 Reflection generated: "Isabella craves community connections to fuel her creative energy"
```

### Research-Grade Memory System
- **Episodic Memory**: Every experience stored with LLM-scored importance
- **Semantic Retrieval**: Find relevant memories using hybrid scoring
- **Automatic Reflection**: Generate insights when experience accumulates

## Key Features

- 🧠 **Cognitive Architecture**: LLM-powered thinking, episodic memory, and automatic reflection
- 🔍 **Hybrid Memory Retrieval**: Semantic similarity + recency + importance scoring
- 🏠 **Local-First**: Runs entirely locally using Ollama—no API keys or cloud dependencies
- 📊 **Persistent Memory**: SQLite for structured data, Chroma for vector search
- 🎨 **Beautiful Terminal UI**: Rich cognitive process visualization with emoji-coded logging
- 🖥️ **Professional CLI**: Complete simulation control and agent inspection
- 📈 **Data Export**: CSV/JSON exports organized by simulation session

## Architecture

```
┌─────────────────────────────────────────┐
│              Simulation Layer           │
│  • Time & tick manager                  │
│  • World state (places, objects)        │
│  • Event bus                            │
├─────────────────────────────────────────┤
│               Agent Layer               │
│  • Memory Stream (Episodic Memory)      │
│  • Retrieval Engine                     │
│  • Reflection Engine                    │
│  • Planning Engine                      │
│  • Action Engine                        │
├─────────────────────────────────────────┤
│            Infrastructure Layer         │
│  • SQLite (structured data)             │
│  • Chroma/FAISS (vector search)         │
│  • Ollama (LLM + embeddings)            │
└─────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) installed and running
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-simulacra-agents
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install Ollama models**
   ```bash
   # Install required models (adjust based on your hardware)
   ollama pull llama3.2:3b
   ollama pull nomic-embed-text
   ```

4. **Initialize the database**
   ```bash
   python scripts/init_db.py
   ```

5. **Start the simulation service**
   ```bash
   python main.py
   ```

## Usage

### Available Commands

The system provides a rich CLI for simulation control and agent inspection:

| Command | Description | Example |
|---------|-------------|---------|
| `python main.py step` | Run one simulation step | See agents think and act |
| `python main.py agent <name>` | Inspect agent details | `python main.py agent isabella` |
| `python main.py agent <name> --memories` | View agent memories | See past experiences |
| `python main.py agent <name> --reflections` | View agent reflections | See insights and self-awareness |
| `python main.py reflect <name>` | Trigger manual reflection | Generate new insights |
| `python main.py status` | Show world state | See all agent locations |

### Example Session: Watching AI Think

**Step 1: Run a simulation step**
```bash
> python main.py step

╭─────────────────────────── 🚀 Simulation Starting ───────────────────────────╮
│  🤖 AI Simulacra Agents v1.0                                                │
│  ✨ 3 agents initialized                                                     │
│  🌍 7 places loaded                                                          │
╰──────────────────────────────────────────────────────────────────────────────╯

╭─────────────────────────── 🤔 Isabella Rodriguez ────────────────────────────╮
│  🧠 Isabella Rodriguez is thinking...                                        │
│  📍 Currently at: Isabella's Apartment                                       │
│  💭 Reasoning: I'm feeling a bit down today, my mood is only 5.0 out of 10,  │
│  and I think it's because I haven't had much social interaction lately...    │
│  ✨ Decision: move to Community Cafe                                         │
╰──────────────────────────────────────────────────────────────────────────────╯

🔍 MEMORY RETRIEVAL: Found 3 relevant memories for isabella
📊 IMPORTANCE SCORED: Isabella Rodriguez memory = 6.5/10
💾 EMBEDDING STORED: isabella memory embedded and indexed
```

**Step 2: Inspect agent memories**
```bash
> python main.py agent isabella --memories

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Isabella Rodriguez ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Recent memories for Isabella Rodriguez:
1. I moved from apartment_1 to cafe. Moved from apartment_1 to Community Cafe 
   (importance: 6.5, action) [16:31]
2. I interact with [WITH JOHN AND MARIA] at Main Street. Performed interact...
   (importance: 7.0, action) [16:31]
```

**Step 3: Watch automatic reflection**
```bash
╭─────────────────────────── 💡 Isabella Rodriguez ────────────────────────────╮
│  🧠 REFLECTION GENERATED                                                     │
│  💭 Generated 3 new insights:                                                │
│  1. **Isabella is craving a sense of community and stability...**            │
│  2. **Isabella's creative energy is fueled by her interactions...**          │
│  3. **Isabella is learning to appreciate downtime and reflection**           │
╰──────────────────────────────────────────────────────────────────────────────╯
```

**Step 4: View reflections**
```bash
> python main.py agent isabella --reflections

Recent reflections for isabella:
1. **Isabella's creative energy is fueled by her interactions with people and environments** 
   (importance: 8.0) [17:01]
   Based on 12 memories
```

## Core Concepts

### 🧠 LLM-Powered Cognition

Our breakthrough achievement: agents use **real LLM reasoning** instead of hard-coded rules.

**Decision Process**:
1. **Context Building**: Current location, energy, recent memories
2. **Memory Retrieval**: Semantically relevant past experiences  
3. **LLM Reasoning**: Natural language thought process
4. **Action Selection**: Choose from move, wait, observe, interact

**Example Agent Reasoning**:
```
"I'm feeling a bit down today, my mood is only 5.0 out of 10, and I think it's 
because I haven't had much social interaction lately. As the owner of the cafe, 
I spend most of my time alone preparing food or dealing with administrative tasks.
I miss the energy and conversation that comes with a bustling community space..."
```

### 💾 Episodic Memory System

**Memory Formation**:
- Every action and observation becomes a memory
- LLM scores importance (0-10 scale)
- Embeddings generated for semantic search
- Stored in SQLite + Chroma vector database

**Memory Types**:
1. **Actions**: What the agent did ("I moved to the cafe")
2. **Observations**: What the agent perceived ("I saw John at the garden")
3. **Reflections**: Self-generated insights ("I crave community connections")

**Hybrid Retrieval**: Combines semantic similarity + recency + importance
```
score = 0.6 × semantic_similarity + 0.2 × recency + 0.2 × importance
```

### ✨ Automatic Reflection System

**Reflection Triggering**:
- Monitors cumulative memory importance (threshold: 15.0)
- Automatically triggers when experiences accumulate
- Can be manually triggered via CLI

**Reflection Process**:
1. **Memory Analysis**: Retrieve high-importance recent memories
2. **Pattern Recognition**: LLM identifies behavioral patterns and insights
3. **Insight Generation**: Creates 3-5 key reflections about the agent
4. **Memory Storage**: Reflections stored as high-importance memories (8.0)

**Example Reflections**:
- *"Isabella is craving a sense of community and stability after transitioning between spaces"*
- *"Isabella's creative energy is fueled by her interactions with people and environments"*

### 🌍 World State & Simulation

**Discrete Time**: 5-minute simulation ticks with agent decision cycles

**World Elements**:
- **Places**: Locations where agents can be present (cafe, apartment, garden, etc.)
- **Objects**: Items agents can interact with (in future milestones)
- **Actions**: move, wait, observe, interact (planning system coming in M5)

**Cognitive Transparency**: Watch every step of agent thinking with emoji-coded logging

## Configuration

### Agent Configuration

Define agents in `config/agents.json`:

```json
{
  "agents": [
    {
      "id": "isabella",
      "name": "Isabella Rodriguez",
      "bio": "Cafe owner who loves hosting community events",
      "home": "apartment_1",
      "personality": "warm, community-minded, creative"
    }
  ]
}
```

### World Configuration

Define places and objects in `config/world.json`:

```json
{
  "places": [
    {
      "id": "cafe",
      "name": "Community Cafe", 
      "description": "A cozy neighborhood cafe",
      "capacity": 20
    }
  ],
  "objects": [
    {
      "id": "espresso_machine",
      "name": "Espresso Machine",
      "location": "cafe",
      "interactions": ["make_coffee", "clean"]
    }
  ]
}
```

## Development

### Project Structure

```
ai-simulacra-agents/
├── agents/              # Agent cognitive modules
│   ├── memory.py       # Memory stream implementation
│   ├── retrieval.py    # Hybrid retrieval engine
│   ├── reflection.py   # Reflection synthesis
│   ├── planning.py     # Hierarchical planning
│   └── acting.py       # Action execution
├── simulation/         # Simulation core
│   ├── world.py        # World state management
│   ├── time_manager.py # Tick management
│   └── events.py       # Event propagation
├── storage/            # Data persistence
│   ├── sqlite_store.py # SQLite operations
│   └── vector_store.py # Vector database
├── api/                # FastAPI service
│   ├── routes.py       # API endpoints
│   └── models.py       # Pydantic schemas
├── cli/                # Terminal interface
│   └── commands.py     # Command handlers
├── config/             # Configuration files
├── tests/              # Test suite
└── scripts/            # Utility scripts
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agents --cov=simulation

# Run specific test file
pytest tests/test_memory.py -v
```

### Code Quality

The project enforces FAANG-level standards:

```bash
# Format code
black .
isort .

# Lint
ruff check .

# Type checking
mypy agents/ simulation/ --strict

# Security scan
bandit -r agents/ simulation/
```

## API Reference

### Core Endpoints

- `POST /simulation/start` - Start simulation
- `POST /simulation/pause` - Pause simulation  
- `POST /simulation/step` - Advance one tick
- `GET /simulation/status` - Get current state
- `GET /agents/{agent_id}` - Get agent details
- `GET /agents/{agent_id}/memories` - Get agent memories
- `POST /agents/{agent_id}/reflect` - Trigger reflection

### Memory API

- `POST /memory/add` - Add new memory
- `GET /memory/query` - Query memories with hybrid retrieval
- `GET /memory/recent` - Get recent memories

## Contributing

1. Follow the established coding standards
2. Add tests for new functionality
3. Update documentation for API changes
4. Use conventional commit messages
5. Ensure all CI checks pass

## 🗺️ Development Status & Roadmap

### ✅ Completed Milestones (5/9)

- **✅ M1: Foundation**: SQLite + Chroma + Ollama integration
- **✅ M2: Agent Actions**: World state, movement, beautiful terminal UI
- **✅ M2.5: LLM Cognition**: Breakthrough—real AI thinking replaces rules
- **✅ M3: Memory System**: Episodic memory with semantic retrieval
- **✅ M4: Reflection**: Automatic self-awareness and insight generation

### 🎯 Current Focus

- **🎯 M5: Planning System**: Goal-oriented behavior and daily/hourly planning
- **📚 M6: Documentation**: This milestone—comprehensive docs and polish

### 🔮 Upcoming Features

- **🎭 M7: Multi-Agent Interactions**: Agent-to-agent communication and social dynamics
- **⚡ M8: Advanced Features**: Optimized retrieval and complex emergent behavior

**What We've Achieved**: From simple rule-based agents to sophisticated AI entities with genuine cognitive behavior, episodic memory, and self-reflection capabilities.

See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for detailed milestones and technical progress.

## License

[Add your license here]

## Acknowledgments

Based on research from "Generative Agents: Interactive Simulacra of Human Behavior" and principles from cognitive architecture research.
