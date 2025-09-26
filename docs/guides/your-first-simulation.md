# Your First Simulation - Complete Walkthrough

> **A detailed, step-by-step guide to understanding and exploring AI agent behavior. Perfect for first-time users who want to really understand what's happening.**

## What You'll Learn

By the end of this guide, you'll understand:
- ✅ How to run and control simulations
- ✅ How to observe and interpret agent behavior  
- ✅ How memory, reflection, and planning work together
- ✅ How to explore agent cognition in depth
- ✅ What makes this different from other AI systems

## Before You Start

Make sure you've completed the [Getting Started](../getting-started.md) guide - you should have:
- ✅ Ollama installed and running
- ✅ The simulation environment set up
- ✅ Successfully run your first `python main.py step`

## Part 1: Understanding the World (5 minutes)

### Meet Your Agents
Your simulation starts with three unique AI characters:

```bash
python main.py status
```

You'll see:
```
🌍 Simulation Status
📅 Current Time: Day 1, 09:00 (Tick 108)
👥 Active Agents: 3

🏠 Agent Locations:
📍 Isabella Rodriguez → Isabella's Apartment 
📍 John Chen → John's Apartment
📍 Maria Santos → Maria's Apartment

🗺️ Available Locations:
• Isabella's Apartment (Cozy studio space)
• John's Apartment (Quiet design studio)  
• Maria's Apartment (Book-filled teacher's home)
• Community Cafe (Isabella's social hub)
• Community Garden (Peaceful outdoor space)
• Local Library (Quiet study environment)
```

### Explore the Characters
Let's meet each agent in detail:

```bash
python main.py agent isabella
```

**Isabella Rodriguez** - Cafe Owner & Community Connector
```
🧠 Personality: Creative, values community connections, seeks social energy
📍 Currently at: Isabella's Apartment
💭 Mood: 5.0/10 (feeling somewhat isolated)
⚡ Energy: 7.5/10 (well-rested but needs social stimulation)

📚 Recent Memories:
1. I woke up in my apartment feeling ready for the day (importance: 3.0)
2. I observed my cozy studio space (importance: 2.5)
```

```bash
python main.py agent john
```

**John Chen** - Introverted Designer
```
🧠 Personality: Introspective, values quiet reflection, seeks creative inspiration
📍 Currently at: John's Apartment  
💭 Mood: 6.5/10 (content but seeking inspiration)
⚡ Energy: 6.0/10 (moderate energy)
```

```bash
python main.py agent maria
```

**Maria Santos** - Community-Minded Teacher
```
🧠 Personality: Social, caring, values helping and connecting others
📍 Currently at: Maria's Apartment
💭 Mood: 7.0/10 (positive and energetic)
⚡ Energy: 8.0/10 (high energy, ready for interaction)
```

### The World Layout
Your agents live in a small community with these locations:
- **Apartments**: Private spaces where agents start each day
- **Community Cafe**: Isabella's business, social gathering spot
- **Community Garden**: Peaceful outdoor space for reflection  
- **Local Library**: Quiet environment for study and thought

## Part 2: Watching AI Minds in Action (10 minutes)

### Your First Decision
Let's watch Isabella make her first real decision:

```bash
python main.py step
```

You'll see something like:
```
╭─────────────────────────── 🤔 Isabella Rodriguez ────────────────────────────╮
│  🧠 Isabella is thinking...                                                  │
│  📍 Currently at: Isabella's Apartment                                       │
│                                                                              │
│  💭 "I'm waking up in my apartment and feeling ready to start the day,      │
│  though my mood is only 5.0 out of 10. I think this is because I haven't    │
│  had much social interaction lately. As someone who owns the Community       │
│  Cafe, I thrive on connecting with people and creating a welcoming space.   │
│  I should head to the cafe to prepare for the day and hopefully encounter   │
│  some community members."                                                    │
│                                                                              │
│  ✨ Decision: I'll move to Community Cafe                                   │
╰──────────────────────────────────────────────────────────────────────────────╯

💾 MEMORY CREATED: Isabella moved from apartment to cafe seeking social connection
🔢 IMPORTANCE SCORED: 6.0/10 (moderately important daily transition)
🧠 EMBEDDING GENERATED: Memory vectorized for future retrieval
📦 STORED: Memory #1 added to Isabella's episodic memory system
```

**🎉 What just happened?** 
- Isabella used real AI to analyze her situation
- She considered her personality, mood, and social needs
- She made an authentic decision based on reasoning
- The experience became a searchable memory

### Understanding the Thinking Process

Let's break down what you just witnessed:

#### 1. **Context Gathering**
The AI considered:
- **Current State**: Location (apartment), mood (5.0/10), energy level
- **Personality**: Community-focused cafe owner who thrives on social connection
- **Recent Experiences**: Limited social interaction lately
- **Goals**: Implicit goal to feel better and connect with community

#### 2. **Reasoning Process** 
The AI used natural language thinking to:
- Analyze the current situation ("mood is only 5.0")
- Identify the likely cause ("haven't had much social interaction")
- Consider personal identity ("someone who owns the Community Cafe")
- Form a plan ("head to the cafe to prepare and encounter community members")

#### 3. **Memory Formation**
The decision became a memory with:
- **Content**: What happened (moved from apartment to cafe)
- **Context**: Why it happened (seeking social connection)
- **Importance**: AI-scored significance (6.0/10)
- **Embedding**: Vector representation for similarity search

### Watch More Agents Think

```bash
python main.py step  # This will process John's turn
```

John's AI thinking might look like:
```
💭 "I'm in my design studio and feeling moderately content, but I'm sensing 
I need some creative inspiration. My recent work has felt a bit stagnant, and 
I know from past experience that changing environments can spark new ideas. 
The Community Garden offers a peaceful setting that often helps me think more 
clearly and connect with natural inspiration."

✨ Decision: I'll move to Community Garden
```

```bash
python main.py step  # This will process Maria's turn
```

Maria's reasoning might be:
```
💭 "I'm feeling energetic and positive this morning. As someone who cares 
deeply about community connections, I'm thinking about how I can help bring 
people together today. Isabella might be preparing the cafe, and that could 
be a great opportunity to support her business while also creating a space 
for community interaction."

✨ Decision: I'll move to Community Cafe
```

### The Magic of Emergent Behavior

Notice how each agent:
- **Thinks differently** based on their unique personality
- **Makes authentic decisions** using real reasoning  
- **Considers their situation** holistically
- **Forms genuine intentions** rather than following scripts

## Part 3: Memory and Learning (10 minutes)

### How Memory Works

Every action creates memories that influence future decisions. Let's explore Isabella's growing memory:

```bash
python main.py agent isabella --memories
```

You'll see her episodic memory system:
```
📚 Recent memories for Isabella:
1. I moved from apartment to cafe seeking social connection (importance: 6.0) [just now]
2. I woke up in my apartment feeling ready for the day (importance: 3.0) [15 minutes ago]
3. I observed my cozy studio space (importance: 2.5) [20 minutes ago]
```

### Watch Memory Influence Decisions

Take several more steps and watch how past experiences influence new choices:

```bash
python main.py step
python main.py step
python main.py step
python main.py agent isabella --memories
```

You might see:
```
📚 Recent memories for Isabella:
1. I interacted with the cafe environment, feeling energized by the space (importance: 5.5) [now]
2. I moved from apartment to cafe seeking social connection (importance: 6.0) [5 min ago]
3. I observed the welcoming atmosphere of my cafe (importance: 4.5) [3 min ago]
4. I waited at the cafe hoping for community members to arrive (importance: 4.0) [2 min ago]
```

### Triggering Self-Reflection

When agents accumulate enough important experiences, they automatically reflect and gain self-awareness:

```bash
python main.py reflect isabella
```

Watch Isabella analyze her own behavior:
```
╭─────────────────────────── 💡 Isabella Rodriguez ────────────────────────────╮
│  🧠 REFLECTION: Analyzing recent experiences...                              │
│                                                                              │
│  💭 Based on my recent memories, I'm noticing some patterns in my behavior:  │
│                                                                              │
│  ✨ Key Insights:                                                            │
│  1. "I consistently seek social environments when my mood is low"            │
│  2. "The cafe serves as both my business and my emotional sanctuary"         │
│  3. "My creative energy is directly linked to community interactions"        │
│                                                                              │
│  🧠 These insights will influence my future decision-making                  │
╰──────────────────────────────────────────────────────────────────────────────╯

💾 REFLECTION STORED: High-importance insights added to memory (importance: 8.5/10)
```

**This is incredible!** Isabella just:
- Analyzed her own behavioral patterns
- Generated authentic psychological insights  
- Created high-importance memories that will guide future decisions
- Developed greater self-awareness

### Memory Retrieval in Action

Now when Isabella makes future decisions, her AI brain will automatically recall relevant memories:

```bash
python main.py step
```

You might see her thinking reference past experiences:
```
💭 "Looking at my recent reflection about seeking social environments when 
my mood is low, and remembering how energized I felt when I moved to the 
cafe earlier, I think I should stay here a bit longer and see if any 
community members arrive. My insight about the cafe being my emotional 
sanctuary feels very true right now."
```

## Part 4: Planning and Goals (10 minutes)

### Autonomous Planning

Agents don't just react - they make plans! Let's see Isabella's daily planning in action:

```bash
python main.py plan isabella
```

You might see:
```
╭───────────────────── 🗓️ Isabella Rodriguez's Daily Plan ─────────────────────╮
│ 📅 Daily Plan for Today                                                     │
│                                                                             │
│ 🎯 Goals for Today:                                                         │
│   1. Connect with community members to boost my mood and energy             │
│   2. Create a welcoming atmosphere at the cafe for social interaction       │
│   3. Take time for personal reflection and creative inspiration             │
│                                                                             │
│ 📋 Hourly Schedule:                                                         │
│   ✅ 09:00-12:00 Morning preparation and community connection at cafe       │
│   🔄 12:00-15:00 Host community gathering and social interaction            │
│   ⏳ 15:00-18:00 Personal time for reflection and creative pursuits         │
│                                                                             │
│ 💭 Plan Status: Active (created 15 minutes ago)                            │
╰─────────────────────────────────────────────────────────────────────────────╯
```

**Amazing!** Isabella created this plan herself using AI reasoning based on:
- Her personality (community-focused cafe owner)
- Her recent memories (seeking social connection)  
- Her reflections (cafe as emotional sanctuary)
- Her current mood and energy levels

### Plan-Aware Decision Making

Now when Isabella makes decisions, she considers her current plans:

```bash
python main.py step
```

Her thinking might reference her plans:
```
💭 "According to my daily plan, I'm in the 'morning preparation and community 
connection' phase at the cafe. This aligns perfectly with my goal to boost 
my mood through social interaction. I should continue activities that support 
this plan while remaining open to community members who might arrive."
```

### Generate New Plans

You can also trigger new planning:

```bash
python main.py plan john --generate
```

Watch John create his own unique daily plan:
```
🎯 John's Goals:
  1. Find creative inspiration for my design work
  2. Spend time in peaceful environments for reflection
  3. Balance solitude with meaningful community moments

📋 Schedule:
  09:00-12:00 Creative work and inspiration-seeking
  12:00-15:00 Quiet reflection and idea development  
  15:00-18:00 Optional community interaction if energy allows
```

## Part 5: Exploring Interactions (15 minutes)

### Social Dynamics

Let's create some interesting social dynamics by getting agents in the same location:

```bash
python main.py step
python main.py step
python main.py step
python main.py status
```

Check if agents are meeting:
```
🏠 Agent Locations:
📍 Isabella Rodriguez → Community Cafe
📍 John Chen → Community Garden  
📍 Maria Santos → Community Cafe
```

If Isabella and Maria are both at the cafe, their next actions will consider each other's presence!

### Observing Social Awareness

When agents are in the same location, their AI thinking becomes socially aware:

```bash
python main.py step
```

Isabella might think:
```
💭 "I notice Maria is here at the cafe! This is perfect - I was hoping for 
community interaction, and Maria always brings such positive energy. As a 
teacher, she has wonderful insights about people and community building. 
This feels like a great opportunity for the meaningful social connection 
I've been seeking."
```

### Complex Emergent Behaviors

Continue running steps and watch for emergent behaviors:
- **Routine Formation**: Agents developing consistent habits
- **Location Preferences**: Certain agents gravitating to specific places
- **Social Patterns**: Agents seeking out or avoiding each other
- **Goal Evolution**: Plans changing based on experiences

```bash
# Run several more steps
python main.py step
python main.py step  
python main.py step
python main.py step
python main.py step

# Check how memories have evolved
python main.py agent isabella --memories
python main.py agent maria --memories
```

## Part 6: Understanding the Data (10 minutes)

### Exporting Simulation Data

Your simulation generates rich data for analysis:

```bash
python main.py export
```

This creates files in the `output/` directory:
- **`agent_actions.csv`** - Every action with reasoning
- **`simulation_state.csv`** - World state at each tick
- **`social_analysis.csv`** - Agent interaction patterns
- **`memory_analysis.csv`** - Memory formation and retrieval
- **`complete_simulation.json`** - Full simulation data

### Reading the Exported Data

Open `agent_actions.csv` to see every decision with full reasoning:
```csv
tick,agent_id,action_type,location,reasoning,importance_score
108,isabella,move,"community_cafe","I'm seeking social connection...",6.0
109,john,move,"community_garden","I need creative inspiration...",5.5
110,maria,move,"community_cafe","I want to support Isabella...",6.5
```

### Understanding Agent Psychology

The memory exports show how agent psychology develops:
```csv
agent_id,memory_content,importance,memory_type,timestamp
isabella,"I crave community connections for creative energy",8.5,reflection,2025-09-26 10:30
john,"Quiet environments help me think more clearly",7.8,reflection,2025-09-26 10:45
maria,"I feel fulfilled when helping others connect",8.2,reflection,2025-09-26 11:00
```

## What You've Discovered

### 🧠 **Authentic AI Cognition**
You've seen agents use real AI to:
- Analyze complex situations using natural language reasoning
- Make decisions based on personality, memories, and goals
- Generate authentic psychological insights through reflection
- Create autonomous plans and pursue personal objectives

### 💾 **Sophisticated Memory Systems**
You've observed how agents:
- Form episodic memories from every experience
- Retrieve relevant past experiences when making decisions
- Use memory importance scoring to prioritize significant events
- Build knowledge through accumulated experiences

### ✨ **Emergent Behavior**
You've witnessed:
- Unique behavioral patterns emerging from each agent's personality
- Social dynamics developing naturally between agents
- Complex decision-making that considers multiple factors
- Unpredictable but psychologically consistent choices

### 🎯 **Goal-Oriented Behavior**
You've seen agents:
- Create their own daily plans and objectives
- Make decisions that align with their personal goals
- Adapt plans based on experiences and reflections
- Balance immediate needs with longer-term intentions

## Next Steps

Now that you understand the core systems, you can:

### 🎮 **Explore Further**
- **[Watch Agent Behavior](watching-cognition.md)** - Advanced observation techniques
- **[Create Custom Agents](customizing-agents.md)** - Design your own AI characters
- **[Run Experiments](running-experiments.md)** - Use for research purposes

### 🧠 **Learn Deeper**
- **[Memory & Learning](../concepts/memory-and-learning.md)** - How the memory system works
- **[Planning & Goals](../concepts/planning-and-goals.md)** - Understanding autonomous planning
- **[The Simulation World](../concepts/the-simulation-world.md)** - How the environment works

### ⚙️ **Customize**
- **[CLI Commands](../reference/cli-commands.md)** - All available commands
- **[Configuration Guide](../reference/configuration.md)** - Customize the simulation
- **[System Architecture](../advanced/architecture-overview.md)** - Technical details

## Congratulations! 🎉

You've just experienced **genuine AI cognition** in action. Unlike traditional simulations with fake "AI" rules, you've witnessed:

- **Real reasoning** generated by language models
- **Authentic memory formation** and retrieval  
- **Genuine self-reflection** and insight generation
- **Autonomous planning** and goal pursuit
- **Emergent social behavior** between AI agents

You're now ready to explore the fascinating world of artificial minds! 🧠✨
