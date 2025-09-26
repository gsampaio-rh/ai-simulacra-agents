# Memory and Learning

> **Just like humans, our AI agents remember everything that happens to them and learn from their experiences. This makes their behavior increasingly sophisticated and realistic over time.**

## How Agent Memory Works

### Every Experience Becomes a Memory

Whenever an agent does something or observes something, it automatically becomes a memory:

```
Isabella's Actions → Isabella's Memories
"I moved to the cafe" → "I moved from apartment to cafe seeking social connection"
"I saw Maria arrive" → "I observed Maria entering the cafe with her warm smile"  
"I felt energized" → "I felt my mood lift from 5.0 to 7.0 after social interaction"
```

Each memory includes:
- **What happened** (the actual event)
- **Why it mattered** (the context and reasoning)
- **How important it was** (AI-scored 0-10 significance)
- **When it occurred** (timestamp for recency)

### Memories Have Different Importance

Not all memories are equally important. The AI automatically scores each memory:

**High Importance (7-10)** - Life-changing moments
- *"I realized I crave community connections to fuel my creative energy"* (8.5)
- *"I had a deep conversation with Maria about our shared community values"* (7.8)

**Medium Importance (4-6)** - Meaningful daily events  
- *"I moved to the cafe seeking social interaction"* (6.0)
- *"I felt energized after seeing other community members"* (5.5)

**Low Importance (1-3)** - Routine activities
- *"I waited at the cafe for 5 minutes"* (3.0)
- *"I observed the familiar cafe environment"* (2.5)

### Smart Memory Retrieval

When agents make decisions, they don't remember everything - they recall the most relevant memories:

**Isabella deciding whether to visit the garden:**
```
🧠 Retrieving relevant memories...
✓ "Last time I felt lonely, the garden's peaceful energy helped" (high relevance)
✓ "John mentioned finding creative inspiration there" (medium relevance)  
✓ "I usually prefer social spaces when my mood is low" (high relevance)
✗ "I had coffee this morning" (low relevance - filtered out)
```

The system combines three factors:
- **Similarity**: How related is this memory to the current situation?
- **Importance**: How significant was this experience?
- **Recency**: How recent was this memory?

## How Learning Happens

### 1. Pattern Recognition Through Reflection

When agents accumulate enough important experiences, they automatically reflect and discover patterns:

```
Isabella's Recent Important Memories:
• Moved to cafe seeking social connection (importance: 6.0)
• Felt energized after seeing Maria (importance: 5.5)  
• Had meaningful conversation with community member (importance: 7.0)
• Felt mood lift from 5.0 to 7.5 after social interaction (importance: 6.5)

🧠 AI Pattern Analysis:
"Looking at these experiences, I notice I consistently seek social 
environments when my mood is low, and my energy directly correlates 
with community interactions. This suggests that social connection is 
not just a preference but a fundamental need for my wellbeing."

✨ Generated Insight:
"I crave community connections to fuel my creative energy"
```

### 2. Insights Influence Future Behavior

These self-generated insights become high-importance memories that guide future decisions:

**Before the insight:**
```
💭 "I'm feeling down. Maybe I should go to the cafe."
(Basic reasoning based on immediate mood)
```

**After the insight:**
```
💭 "I'm feeling down, and my reflection revealed that I crave community 
connections to fuel my creative energy. Based on this understanding of 
myself, the cafe would be perfect for both improving my mood and 
inspiring my creative work."
(Sophisticated reasoning incorporating self-knowledge)
```

### 3. Memory-Informed Planning

Agents use their accumulated memories and insights to create better plans:

**John's Planning Process:**
```
🧠 Reviewing memories about creative inspiration...
• "Quiet garden environment helped me think clearly" (importance: 6.5)
• "Interruptions at home disrupted my design flow" (importance: 5.0)  
• "Best ideas came during peaceful morning hours" (importance: 7.0)

📝 Generated Plan:
09:00-12:00 Creative work at Community Garden (quiet morning environment)
12:00-15:00 Design development at home (less interruption risk)
15:00-18:00 Community time if energy allows (balance solitude with connection)
```

## Types of Learning

### 🎯 **Behavioral Learning**
Agents discover what actions lead to desired outcomes:

- *"Moving to the cafe when I feel isolated consistently improves my mood"*
- *"Visiting the garden helps John find creative inspiration"*
- *"Maria feels most fulfilled when organizing community activities"*

### 🧠 **Self-Knowledge Learning**  
Agents develop deeper understanding of their own psychology:

- *"I'm happiest when I can combine solitude with meaningful social moments"*
- *"My creative energy is directly linked to my social connections"*
- *"I need both quiet reflection time and community interaction to thrive"*

### 🤝 **Social Learning**
Agents learn about other agents and social dynamics:

- *"Isabella becomes more energetic when community members visit her cafe"*
- *"John appreciates brief, meaningful interactions rather than extended socializing"*
- *"Maria has insights about bringing people together effectively"*

### 🌍 **Environmental Learning**
Agents discover how different locations affect them:

- *"The cafe provides social energy but can be overstimulating when busy"*
- *"The garden offers peaceful inspiration but can feel isolating"*
- *"The library combines quiet focus with subtle community presence"*

## Watching Learning in Action

### Memory Formation
```bash
python main.py step
```
```
💾 Creating memory: Isabella had meaningful conversation with Maria (importance: 7.0/10)
🧠 Memory embedded and stored for future recall
```

### Automatic Reflection
```bash
python main.py reflect isabella
```
```
💡 New insight: "I consistently seek social environments when my mood drops, 
suggesting that community connection is essential for my emotional wellbeing."
```

### Memory-Influenced Decisions
```bash
python main.py step
```
```
💭 "Based on my recent insight about needing social connection for wellbeing, 
and remembering how energized I felt after yesterday's conversation with Maria, 
I should visit the cafe where I'm most likely to encounter community members."
```

### Plan Adaptation
```bash
python main.py plan isabella
```
```
🗓️ Updated Daily Plan (incorporating recent learning):
🎯 Goal: Prioritize community connection as foundation for creative energy
📋 Schedule: 
- Morning: Social preparation at cafe  
- Afternoon: Community hosting and interaction
- Evening: Creative work energized by social connection
```

## Why This Matters

### 🎭 **Authentic Character Development**
Unlike scripted characters, agents genuinely evolve:
- Personalities deepen through self-discovery
- Behavioral patterns emerge naturally  
- Relationships develop based on real interactions
- Growth feels organic and believable

### 🔬 **Research Applications**
Researchers can study:
- How memory systems affect AI behavior
- Emergence of personality through experience
- Social learning and relationship formation
- Long-term behavioral adaptation

### 🎮 **Engaging Experience**
Users enjoy:
- Watching characters grow and change
- Discovering emergent behavioral patterns
- Seeing the impact of different experiences
- Understanding how AI minds develop

## Advanced Memory Features

### Memory Consolidation
Over time, related memories combine into higher-level insights:
```
Individual memories: "Cafe visit 1", "Cafe visit 2", "Cafe visit 3"
    ↓
Consolidated insight: "The cafe is my primary social energy source"
```

### Emotional Memory Weighting
Emotionally significant events get stronger memory encoding:
```
Neutral event: "I moved to the library" (importance: 3.0)
Emotional event: "I felt deeply connected during our community gathering" (importance: 8.5)
```

### Cross-Agent Memory Sharing
Agents can learn from observing others' experiences:
```
John observes: "Isabella seems happiest when the cafe is busy with community members"
John's memory: "Social environments energize some people differently than they do me"
```

## Next Steps

- **[Planning & Goals](planning-and-goals.md)** - How memory influences planning
- **[The Simulation World](the-simulation-world.md)** - How environment shapes memory
- **[Watch Agent Behavior](../guides/watching-cognition.md)** - Observe memory in action
- **[Running Experiments](../guides/running-experiments.md)** - Study memory and learning
