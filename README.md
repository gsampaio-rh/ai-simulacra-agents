# AI Simulacra Agents

A foundational simulation layer for autonomous generative agents that perceive, remember, reflect, plan, and act in a simulated world. Built for local development with terminal-only interaction and no cloud dependencies.

## Overview

This project implements the core architecture for agent simulation based on memory streams, reflection, and hierarchical planning. Agents operate in discrete time ticks, maintaining episodic memory with semantic retrieval, and can interact with each other and their environment.

### Key Features

- 🧠 **Cognitive Architecture**: Memory streams, reflection synthesis, and hierarchical planning
- 🔍 **Hybrid Retrieval**: Combines semantic similarity, recency, and importance scoring
- 🏠 **Local-First**: Runs entirely locally using Ollama for LLM and embedding tasks
- 📊 **Persistent Memory**: SQLite for structured data, Chroma/FAISS for vector search
- ⚡ **FastAPI Service**: RESTful orchestration of simulation ticks and agent interactions
- 🖥️ **Terminal-Based**: Full control via CLI commands, no GUI dependencies

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
   ollama pull llama2:7b
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

### Terminal Commands

Once the simulation is running, use these commands:

| Command | Description |
|---------|-------------|
| `start` | Start the simulation loop |
| `pause` | Pause simulation |
| `step` | Advance by one tick |
| `status` | Print world state and agent locations |
| `agent <id>` | Show details for specific agent |
| `mem <id>` | Dump recent memories for agent |
| `reflect <id>` | Trigger reflection for agent |
| `plan <id>` | Show current plan for agent |
| `exit` | Shut down simulation cleanly |

### Example Session

```bash
> start
[T+0] Simulation started with 3 agents
[T+0] Isabella moves from Apartment to Cafe
[T+5] Isabella says to John: "Good morning!"
[T+10] John replies: "Morning! Did you hear about the party?"

> pause
Simulation paused at T+15

> agent isabella
Agent: Isabella
Location: Cafe
Current Task: Having morning coffee
Energy: 85/100
Recent Actions: moved to Cafe, greeted John

> mem isabella
Recent memories for Isabella:
[T+10] John mentioned a party (importance: 7)
[T+5] Greeted John at the cafe (importance: 4)
[T+0] Left apartment for morning routine (importance: 3)
```

## Core Concepts

### Memory System

Each agent maintains two types of memory:

1. **Episodic Memory**: Raw perceptions and experiences stored with timestamps and importance scores
2. **Reflections**: Synthesized insights created when memory importance crosses a threshold

### Retrieval Scoring

Memories are retrieved using a weighted formula:
```
score = α × semantic_similarity + β × recency + γ × importance
```
Default weights: α=0.6, β=0.2, γ=0.2

### Planning Hierarchy

Agents plan in three levels:
- **Day Plans**: High-level goals and activities
- **Hourly Blocks**: Specific time-bound activities  
- **Tasks**: 5-15 minute executable actions

### World State

The simulation maintains:
- **Places**: Locations where agents can be present
- **Objects**: Items that can be interacted with
- **Events**: Observable actions that generate perceptions

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

## Roadmap

- **M1 Foundation**: SQLite + Chroma + Ollama integration
- **M2 Agent Core**: Memory stream + retrieval + reflection  
- **M3 Simulation**: World state + tick manager + acting
- **M4 Terminal UX**: Complete CLI command set
- **M5 MVP**: Multi-agent interactions

See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for detailed milestones.

## License

[Add your license here]

## Acknowledgments

Based on research from "Generative Agents: Interactive Simulacra of Human Behavior" and principles from cognitive architecture research.
