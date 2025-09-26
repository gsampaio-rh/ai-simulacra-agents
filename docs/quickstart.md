# Quick Start Guide

Get your AI agents thinking, remembering, reflecting, and planning in just 5 minutes! This guide will have you running autonomous cognitive agents with breakthrough LLM-powered behavior.

## 🎯 What You'll Achieve

By the end of this guide, you'll have:
- ✅ Autonomous agents with real AI cognition
- ✅ Beautiful terminal interface showing agent thinking
- ✅ Agents forming memories, reflecting, and planning
- ✅ Complete cognitive transparency and control

## ⚡ Prerequisites (2 minutes)

1. **Python 3.10+** installed
2. **[Ollama](https://ollama.ai/)** installed and running
3. **Git** for cloning the repository

### Install Ollama (if needed)
```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: Download from https://ollama.ai/
```

## 🚀 Step 1: Setup (2 minutes)

### Clone and Install
```bash
# Clone the repository
git clone [repository-url]
cd ai-simulacra-agents

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Install AI Models
```bash
# Install the LLM (adjust model based on your hardware)
ollama pull llama3.2:3b      # Good for most systems
# ollama pull llama3.2:1b    # For lower-end hardware
# ollama pull llama3.2:8b    # For high-end systems

# Install embedding model
ollama pull nomic-embed-text
```

### Initialize Database
```bash
python scripts/init_db.py
```

## 🧠 Step 2: Your First Agents (1 minute)

### Start a Simulation Step
```bash
python main.py step
```

**You'll see something amazing** - real AI thinking in action:

```
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

🎉 **Congratulations!** Your agents are thinking with real AI cognition!

## 🔍 Step 3: Explore Agent Cognition (2 minutes)

### Inspect Agent Details
```bash
python main.py agent isabella
```

You'll see a beautiful display with:
- **Agent personality** and background
- **Current state** (location, energy, mood)
- **Planning status** (goals and current tasks)
- **Recent memories** with importance scores

### View Agent's Daily Plan
```bash
python main.py plan isabella
```

See the agent's autonomous planning:
```
╭───────────────────── 🗓️ Isabella Rodriguez's Daily Plan ─────────────────────╮
│ 📅 Daily Plan for 2025-09-26                                                │
│ 🎯 Goals for Today:                                                         │
│   1. To take a moment for self-care, recharge, and connect with my          │
│   community by hosting an intimate gathering at the cafe.                   │
│ 📋 Schedule:                                                                │
│   ✅ 09:00 - 12:00 - Take some time for self-care by practicing yoga...     │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### Watch Memory Formation
```bash
python main.py agent isabella --memories
```

See how agents remember everything:
```
Recent memories for isabella:
1. I moved from apartment_1 to cafe. (importance: 6.5, action) [14:32]
2. I observed my surroundings at Community Cafe. (importance: 4.0, action) [14:31]
3. I waited for 5 minutes at Isabella's Apartment. (importance: 4.0, action) [14:30]
```

### Trigger Reflection
```bash
python main.py reflect isabella
```

Watch the agent gain self-awareness:
```
╭─────────────────────────── 💡 Isabella Rodriguez ────────────────────────────╮
│  🧠 REFLECTION GENERATED                                                     │
│  💭 Generated 3 new insights:                                                │
│  1. **Isabella is craving a sense of community and connection**              │
│     Her repeated moves between cafe and apartment suggest she's searching... │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## 🎮 Next Steps: Explore More

### Run Multiple Steps
```bash
# Run several simulation steps
python main.py step
python main.py step
python main.py step
```

### Explore All Agents
```bash
python main.py agent john      # The introverted designer
python main.py agent maria     # The community-oriented teacher
```

### Check World Status
```bash
python main.py status
```

### Generate New Plans
```bash
python main.py plan john --generate
```

## 🎯 What You've Experienced

### Breakthrough Cognitive Architecture
Your agents demonstrate genuine AI cognition:

1. **🧠 Real LLM Thinking**: Natural language reasoning, not rules
2. **💾 Episodic Memory**: Experience storage with semantic retrieval
3. **✨ Automatic Reflection**: Self-awareness and insight generation
4. **🎯 Autonomous Planning**: Goal-oriented daily planning
5. **🎨 Beautiful UI**: Complete cognitive transparency

### Key Differences from Traditional Systems
```
❌ Traditional: if mood < 5: goto("social_area")
✅ Our System: "I'm feeling down today because I haven't had much 
               social interaction. As a cafe owner, I should..."
```

## 🚀 Ready for More?

### Deep Dive Options
- **[Cognitive Architecture](cognitive-architecture.md)** - How the AI cognition works
- **[CLI Reference](api/cli-reference.md)** - All available commands
- **[Agent Configuration](guides/agent-configuration.md)** - Create custom agents
- **[Advanced Examples](examples/advanced-scenarios.md)** - Complex scenarios

### Research & Development
- **[Research Documentation](research/methodology.md)** - Academic use
- **[Development Guide](guides/development.md)** - Contributing to the project
- **[Architecture Deep Dive](../ARCHITECTURE.md)** - Technical details

## 🎉 Congratulations!

You now have **autonomous cognitive agents** with:
- Real AI thinking and reasoning
- Persistent episodic memory
- Automatic self-reflection
- Autonomous daily planning
- Beautiful cognitive transparency

**Your agents are truly thinking, remembering, reflecting, and planning!** 🧠✨🎯

---

**Questions?** Check our [documentation index](README.md) or explore the [examples](examples/) directory!
