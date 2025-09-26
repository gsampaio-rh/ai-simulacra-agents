# Getting Started - See AI Minds in 5 Minutes! 

> **From zero to watching AI characters think, remember, and make decisions in just 5 minutes.**

## What You'll Experience

By the end of this guide, you'll have:
- ✅ AI characters making their own decisions in real-time
- ✅ Beautiful displays showing exactly how they think
- ✅ Agents remembering experiences and forming insights
- ✅ A complete working simulation on your computer

## Step 1: Install the Basics (2 minutes)

### What You Need
- **Python 3.10+** (check with `python --version`)
- **5 GB free space** for AI models
- **Internet connection** for initial setup

### Install Ollama (The AI Brain)
```bash
# macOS/Linux - one command installs everything
curl -fsSL https://ollama.ai/install.sh | sh

# Windows - download from https://ollama.ai/
```

That's it! Ollama runs the AI locally on your computer - no cloud, no API keys needed.

## Step 2: Get the Simulation Running (2 minutes)

### Download and Setup
```bash
# Get the code
git clone [repository-url]
cd ai-simulacra-agents

# Create a safe environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install everything
pip install -r requirements.txt
```

### Download the AI Models
```bash
# Install the AI brain (choose based on your computer)
ollama pull llama3.2:3b      # Good for most computers (4GB+ RAM)
# ollama pull llama3.2:1b    # Slower computers (2GB+ RAM)  
# ollama pull llama3.2:8b    # Powerful computers (16GB+ RAM)

# Install the memory system
ollama pull nomic-embed-text
```

### Initialize Your World
```bash
python scripts/init_db.py
```

## Step 3: Meet Your First AI Agent (1 minute)

### Start the Simulation
```bash
python main.py step
```

**🎉 Magic happens!** You'll see something like this:

```
╭─────────────────────────── 🤔 Isabella Rodriguez ────────────────────────────╮
│  🧠 Isabella is thinking...                                                  │
│  📍 Currently at: Isabella's Apartment                                       │
│                                                                              │
│  💭 "I'm feeling a bit down today, my mood is only 5.0 out of 10, and I     │
│  think it's because I haven't had much social interaction lately. As the     │
│  owner of the cafe, I spend most of my time alone. Maybe I should go to      │
│  the Community Garden where I might encounter some neighbors."               │
│                                                                              │
│  ✨ Decision: I'll move to Community Garden                                  │
╰──────────────────────────────────────────────────────────────────────────────╯

💾 Creating memory: Isabella moved from apartment to garden (importance: 6.5/10)
🧠 Memory embedded and stored for future recall
```

**That reasoning was generated live by AI!** Isabella actually thought about her situation and made an authentic decision.

## Step 4: Explore AI Cognition (2 minutes)

### See Inside an Agent's Mind
```bash
python main.py agent isabella
```

You'll see Isabella's complete mental state:
- 🧠 **Personality & background**
- 📍 **Current location and mood**  
- 💭 **Recent memories with importance scores**
- 🎯 **Current plans and goals**

### Watch Memory Formation
```bash
python main.py step  # Take another step
python main.py agent isabella --memories
```

See how every action becomes a memory:
```
Recent memories for Isabella:
1. I moved from apartment to garden seeking social connection (importance: 6.5) [just now]
2. I observed the peaceful garden environment (importance: 4.0) [2 minutes ago]  
3. I waited at home feeling isolated (importance: 3.0) [5 minutes ago]
```

### Trigger Self-Reflection
```bash
python main.py reflect isabella
```

Watch Isabella gain self-awareness:
```
╭─────────────────────────── 💡 Isabella Rodriguez ────────────────────────────╮
│  🧠 REFLECTION: Analyzing recent experiences...                              │
│                                                                              │
│  ✨ New Insights:                                                            │
│  1. "I crave community connections to fuel my creative energy"               │
│  2. "My mood directly correlates with social interaction levels"             │
│  3. "I'm learning to recognize and address my need for connection"           │
╰──────────────────────────────────────────────────────────────────────────────╯
```

These insights will influence Isabella's future decisions!

### See Her Plans
```bash
python main.py plan isabella
```

View Isabella's autonomous daily planning:
```
📅 Isabella's Daily Plan
🎯 Today's Goals:
   • Connect with community members and recharge social energy
   • Maintain the cafe as a welcoming community space

📋 Schedule:
   ✅ 09:00-12:00 Morning self-care and reflection
   🔄 12:00-15:00 Visit community spaces for social interaction  
   ⏳ 15:00-18:00 Cafe preparation and hosting
```

## What Just Happened? 🤯

You witnessed **real AI cognition** in action:

### 🧠 **Authentic Thinking**
Isabella didn't follow pre-programmed rules. She used real AI to reason about her situation, consider her feelings, and make a decision.

### 💾 **Genuine Memory**
Every experience becomes a searchable memory. Isabella can recall past events when making new decisions, just like humans do.

### ✨ **Self-Awareness**
Isabella reflects on her experiences and forms insights about herself. These insights influence her future behavior.

### 🎯 **Autonomous Planning**  
Isabella creates her own daily plans based on her personality, memories, and reflections. No human wrote these plans!

## What's Next?

### 🎮 **Explore More**
```bash
python main.py agent john      # Meet John, the introverted designer
python main.py agent maria     # Meet Maria, the community teacher
python main.py status          # See the whole simulation world
```

### 📚 **Learn Deeper**
- **[How Agents Think](concepts/how-agents-think.md)** - Understand the AI cognition system
- **[Complete User Guide](guides/your-first-simulation.md)** - Detailed walkthrough
- **[Examples & Use Cases](examples/)** - See what's possible

### 🛠️ **Customize**
- **[Create Custom Agents](guides/customizing-agents.md)** - Design your own AI characters
- **[Run Experiments](guides/running-experiments.md)** - Use for research
- **[All CLI Commands](reference/cli-commands.md)** - Complete command reference

## Troubleshooting

**Ollama not found?** Make sure it's installed and running: `ollama serve`

**Python errors?** Check you have Python 3.10+: `python --version`

**Models too slow?** Try a smaller model: `ollama pull llama3.2:1b`

**Need help?** Check our **[Troubleshooting Guide](guides/troubleshooting.md)**

---

**🎉 Congratulations!** You've just witnessed artificial minds thinking, remembering, and planning autonomously. Welcome to the future of AI simulation!
