# Cognitive Architecture

This document provides a comprehensive overview of the breakthrough cognitive architecture that powers our AI agents. Unlike traditional rule-based systems, our agents possess genuine cognitive capabilities through real LLM-powered reasoning.

## 🧠 Overview: The Cognitive Stack

Our agents implement a complete cognitive architecture inspired by human cognition:

```
📊 COGNITIVE LAYER STACK

5. 🎯 PLANNING LAYER     ← Goals and daily planning
   ├─ Goal generation    ← "I want to connect with community"
   ├─ Time blocking      ← "9-12: Self-care at cafe"
   └─ Plan execution     ← Guides decision-making

4. ✨ REFLECTION LAYER   ← Self-awareness and insights
   ├─ Pattern recognition ← "I often seek social interaction"
   ├─ Insight generation  ← "I crave community connections"
   └─ Self-understanding  ← High-importance memories (8.0)

3. 💾 MEMORY LAYER       ← Experience storage and retrieval
   ├─ Memory formation   ← Every action/observation stored
   ├─ Importance scoring ← LLM evaluates significance (0-10)
   ├─ Embedding creation ← Vector representations for similarity
   └─ Hybrid retrieval   ← Semantic + recency + importance

2. 🧠 COGNITION LAYER    ← Real AI reasoning and thinking
   ├─ Context building   ← Current situation + memories
   ├─ LLM reasoning      ← Natural language thought process
   └─ Decision making    ← Authentic choice with explanation

1. 👁️ PERCEPTION LAYER   ← Environment awareness
   ├─ World observation  ← Current location, agents, objects
   ├─ State monitoring   ← Energy, mood, current task
   └─ Context awareness  ← Time, recent events, planning
```

## 🔄 The Cognitive Loop

Every agent tick follows a complete cognitive cycle:

```
1. PERCEIVE → 2. REMEMBER → 3. REFLECT → 4. PLAN → 5. THINK → 6. ACT
     ↓            ↓           ↓          ↓        ↓        ↓
  Observe      Retrieve    Generate   Update   Reason   Execute
  current      relevant    insights   goals    through  action
  context      memories    (auto)     (auto)   LLM      choice
     ↓            ↓           ↓          ↓        ↓        ↓
  Location,    Semantic    Pattern    Daily    "I feel  Move to
  energy,      search +    analysis   plan     down     Community
  mood,        importance  of high-   based    and      Cafe
  agents       scoring     value      on       need     (with
                          memories    context  social   reasoning)
                                               contact"
```

## 🧠 1. LLM-Powered Cognition Engine

### Core Innovation: Real AI Reasoning

**The Breakthrough**: Our agents use actual LLM reasoning for decisions, not pre-programmed rules.

```python
# ❌ Traditional Rule-Based System:
if agent.mood < 5.0 and agent.personality == "social":
    return MoveTo("social_area")

# ✅ Our LLM-Powered System:
reasoning = llm.generate(f"""
You are {agent.name}, currently at {location} with mood {mood}/10.
Recent memories: {relevant_memories}
Current plan: {daily_plan}
What would you naturally want to do next?
""")
# Result: "I'm feeling down because I haven't had social interaction lately.
#          As a cafe owner, I should visit the community space..."
```

### Decision Process Flow

**1. Context Building**
```python
context = {
    "current_location": "Isabella's Apartment",
    "energy": 100.0,
    "mood": 5.0,
    "other_agents": ["john", "maria"] if at_social_location else [],
    "recent_memories": retrieval_engine.get_relevant(query, limit=3),
    "current_plan": planning_engine.get_current_task(),
    "personality": "warm, community-minded, creative, empathetic"
}
```

**2. LLM Reasoning**
```
Input: Rich context about agent's situation, memories, and plans
Process: Natural language reasoning by LLM
Output: Authentic thought process + chosen action
```

**3. Action Selection**
- **move** - Navigate to connected locations
- **wait** - Rest and recover energy
- **observe** - Examine surroundings and other agents
- **interact** - Engage with environment or agents

### LLM Integration Points

**Decision Making**:
- Natural language reasoning for action choices
- Context-aware responses based on personality
- Memory-informed decision making

**Memory Importance Scoring**:
```python
importance = llm.evaluate(f"""
Rate the importance of this memory for {agent.name} (0-10):
Memory: "{memory_content}"
Context: {agent_personality}
""")
# Returns: 7.5 (for significant social interaction)
```

**Reflection Generation**:
- Pattern recognition in agent behavior
- Insight synthesis from multiple memories
- Self-awareness development

**Plan Creation**:
- Goal-oriented daily planning
- Personality-driven objectives
- Context-informed scheduling

## 💾 2. Episodic Memory System

### Memory Formation Pipeline

Every agent experience becomes a persistent memory:

```
ACTION/OBSERVATION → IMPORTANCE SCORING → EMBEDDING → STORAGE
       ↓                     ↓               ↓          ↓
"I moved to cafe"      LLM evaluates     Vector for   SQLite +
(raw experience)       significance      similarity   Chroma
                       (6.5/10)          search       (persistent)
```

### Memory Types

**1. Action Memories**
```json
{
  "type": "action",
  "content": "I moved from apartment_1 to cafe",
  "importance": 6.5,
  "timestamp": "2025-09-26T14:32:00",
  "metadata": {
    "action_type": "move",
    "from": "apartment_1",
    "to": "cafe"
  }
}
```

**2. Observation Memories**
```json
{
  "type": "observation", 
  "content": "I observed my surroundings at Community Cafe",
  "importance": 4.0,
  "metadata": {
    "location": "cafe",
    "other_agents": ["maria"],
    "objects": ["espresso_machine", "art_displays"]
  }
}
```

**3. Reflection Memories**
```json
{
  "type": "reflection",
  "content": "I crave community connections to fuel my creative energy",
  "importance": 8.0,
  "metadata": {
    "insight_type": "self_awareness",
    "based_on_memories": ["mem_1", "mem_2", "mem_3"],
    "pattern": "social_seeking_behavior"
  }
}
```

### Hybrid Retrieval Algorithm

**Smart Memory Retrieval**: Combines three scoring dimensions:

```python
def calculate_relevance(memory, query, current_time):
    # 1. Semantic Similarity (60% weight)
    semantic_score = cosine_similarity(
        embed(query), 
        memory.embedding
    )
    
    # 2. Recency Score (20% weight) 
    hours_since = (current_time - memory.timestamp).hours
    recency_score = math.exp(-hours_since / 24)  # Decay over time
    
    # 3. Importance Score (20% weight)
    importance_score = memory.importance / 10.0
    
    # Combined relevance
    return (
        0.6 * semantic_score +
        0.2 * recency_score +
        0.2 * importance_score
    )
```

**Example Query**: "I'm feeling isolated and want social interaction"

```
Retrieval Results:
1. "I had a satisfying conversation with Maria" (relevance: 0.85)
   ├─ Semantic: 0.92 (high similarity to social interaction)
   ├─ Recency: 0.78 (happened yesterday)
   └─ Importance: 0.75 (scored 7.5/10)

2. "I reflected: I crave community connections" (relevance: 0.83)
   ├─ Semantic: 0.89 (matches social themes)
   ├─ Recency: 0.65 (few days ago)
   └─ Importance: 0.80 (reflection, high importance)
```

## ✨ 3. Automatic Reflection Engine

### Reflection Triggering

**Threshold-Based Activation**:
```python
def should_reflect(agent):
    # Monitor cumulative importance of recent memories
    recent_memories = get_memories_since_last_reflection(agent)
    total_importance = sum(m.importance for m in recent_memories)
    
    return total_importance >= 15.0  # Trigger threshold
```

**Example Trigger Scenario**:
```
Memory Accumulation:
├─ "Moved to cafe" (importance: 6.5)
├─ "Interacted with Maria" (importance: 7.0) 
├─ "Observed busy cafe" (importance: 4.5)
└─ Total: 18.0 ≥ 15.0 → Trigger reflection!
```

### Reflection Process

**1. Memory Analysis**
```python
# Gather high-importance recent memories
reflection_memories = [
    m for m in recent_memories 
    if m.importance >= 6.0
][:20]  # Top 20 memories
```

**2. Pattern Recognition**
```
LLM Input: "Analyze these memories for patterns:
- Isabella moved to cafe (importance: 6.5)
- Isabella talked with Maria about community (importance: 7.0)
- Isabella observed thriving social space (importance: 6.2)
- Isabella felt energized by interactions (importance: 7.5)

What behavioral patterns do you see?"
```

**3. Insight Generation**
```
LLM Output: 3 key reflections:
1. **Isabella craves community connections to fuel her creative energy**
2. **Isabella finds meaning in facilitating social interactions**
3. **Isabella's mood improves significantly in collaborative environments**
```

**4. Memory Storage**
Each reflection becomes a high-importance memory (8.0) that influences future decisions.

### Reflection Impact on Behavior

**Before Reflection**:
```
Agent thinks: "I'm at my apartment. I could wait here or move somewhere."
Decision: Random-seeming movement
```

**After Reflection** ("I crave community connections"):
```
Agent thinks: "I'm feeling isolated. My recent reflection showed I thrive 
on community connections. The cafe would be perfect for meeting people."
Decision: Purposeful movement to social spaces
```

## 🎯 4. Autonomous Planning System

### Planning Architecture

**Hierarchical Structure**:
```
DailyPlan
├── Goals: ["Connect with community", "Practice self-care"]
├── HourlyBlock (09:00-12:00)
│   ├── Activity: "Morning self-care routine"
│   ├── Location: "Cafe (quiet corner)"
│   └── Tasks: [
│       Task("Practice yoga", duration=30, location="cafe"),
│       Task("Meditation time", duration=20, location="cafe"),
│       Task("Journaling", duration=25, location="cafe")
│   ]
├── HourlyBlock (13:00-17:00)
│   ├── Activity: "Community engagement"
│   └── Tasks: [...]
└── Status: Active
```

### Planning Triggers (Autonomous)

**1. No Current Plan**
```python
if not agent.current_plan:
    trigger_planning("No active daily plan")
```

**2. Stale Plan**
```python
if plan_age > timedelta(hours=6):
    trigger_planning("Plan is outdated")
```

**3. Significant New Experiences**
```python
new_high_importance_memories = count_memories_since_plan(importance >= 7.0)
if new_high_importance_memories >= 3:
    trigger_planning("Major new experiences require plan update")
```

### Planning Process

**1. Context Analysis**
```python
planning_context = {
    "personality": agent.personality,
    "recent_memories": get_recent_memories(limit=10),
    "reflection_insights": get_recent_reflections(limit=5),
    "current_energy": agent.energy,
    "current_mood": agent.mood,
    "time_of_day": current_time,
    "available_locations": world.get_connected_places(agent.location)
}
```

**2. LLM Plan Generation**
```
LLM Prompt: "Create a daily plan for Isabella Rodriguez:

Personality: warm, community-minded, creative, empathetic, organized
Recent reflection: 'I crave community connections to fuel my creative energy'
Current mood: 5.0/10 (needs uplifting)
Available locations: apartment, cafe, garden, main_street

Generate 2-3 goals and a schedule with specific time blocks."
```

**3. Plan Structuring**
```
LLM Output → Parsed into:
├── Goals extraction: ["Self-care and recharge", "Connect with community"]
├── Time block creation: HourlyBlock objects with start/end times
├── Task breakdown: Specific actionable items
└── Location assignment: Where each activity should happen
```

### Plan-Aware Decision Making

**Integration with Cognition**:
```python
def make_decision(agent, context):
    # Include current plan in decision context
    current_plan = planning_engine.get_current_plan(agent)
    current_task = planning_engine.get_current_task(agent)
    
    prompt = f"""
    You are {agent.name}. Current situation: {context}
    
    Your daily goals: {current_plan.goals if current_plan else "None"}
    Current planned task: {current_task.description if current_task else "None"}
    
    What would you like to do next? Consider your plans while staying 
    flexible and authentic to your personality.
    """
    
    return llm.generate(prompt)
```

**Example Plan-Influenced Decision**:
```
Context: Isabella is at apartment, energy 100%, mood 5.0
Plan: Current task is "Practice yoga and meditation (at cafe)"
Location: Currently at apartment

Decision: "My plan suggests practicing yoga at the cafe. This aligns 
perfectly with my need for self-care while being in a community space. 
I'll head to the cafe now."

Action: move(destination="cafe")
```

## 🔄 5. Cognitive Integration

### Cross-System Interactions

**Memory → Reflection**:
```python
# High-importance memories accumulate
total_importance = sum(memory.importance for memory in recent_memories)
if total_importance >= 15.0:
    trigger_reflection()
```

**Reflection → Planning**:
```python
# Insights inform plan generation
reflection_insights = ["I crave community connections", "I need creative outlets"]
planning_context["insights"] = reflection_insights
generate_plan(planning_context)
```

**Planning → Action**:
```python
# Current plans influence decisions
current_task = "Practice yoga at cafe"
decision_context["current_plan_task"] = current_task
action = llm_behavior.choose_action(agent, decision_context)
```

**Action → Memory**:
```python
# Every action creates new memories
action_result = execute_action(action)
memory = create_memory(
    content=f"I {action.type} {action.description}",
    importance=llm.score_importance(action_result),
    metadata=action_result.metadata
)
store_memory(memory)
```

### Emergent Behaviors

The cognitive architecture enables sophisticated emergent behaviors:

**1. Goal Persistence**
- Agents develop consistent objectives across sessions
- Plans evolve but maintain personality-driven themes

**2. Memory-Informed Growth**
- Past experiences genuinely influence future decisions
- Agents learn from mistakes and successes

**3. Authentic Personality Expression**
- LLM reasoning ensures actions align with defined personality
- Consistent character traits emerge naturally

**4. Adaptive Planning**
- Plans update based on new experiences and reflections
- Flexible execution allows for spontaneous authentic behavior

## 🧪 Validation & Research

### Cognitive Authenticity Metrics

**1. Decision Coherence**
- Measure consistency between personality, memories, and actions
- Track goal-oriented behavior patterns

**2. Memory Integration**
- Verify that past experiences influence future decisions
- Analyze semantic coherence in memory retrieval

**3. Reflection Quality**
- Evaluate insight generation accuracy
- Measure behavioral changes after reflection

**4. Planning Effectiveness**
- Track goal achievement and plan completion
- Analyze plan adaptation to new circumstances

### Research Applications

**Cognitive Science Research**:
- Study memory formation and retrieval patterns
- Analyze reflection and insight generation processes
- Investigate planning and goal-oriented behavior

**AI Behavior Analysis**:
- Compare LLM reasoning vs rule-based decisions
- Study emergent personality expression
- Analyze multi-agent social dynamics (upcoming M7)

**Human-AI Interaction Studies**:
- Test agent believability and authenticity
- Study user engagement with cognitive transparency
- Analyze trust building through explainable AI

## 🚀 Future Enhancements

### Planned Cognitive Improvements

**M7: Social Cognition** (Next milestone)
- Agent-to-agent memory sharing
- Social relationship modeling
- Collaborative planning and group dynamics

**M8: Advanced Cognition**
- Emotional state modeling
- Long-term goal persistence
- Complex reasoning chains

**Research Extensions**
- Personality development over time
- Learning from multi-agent interactions
- Cultural and social norm emergence

---

This cognitive architecture represents a breakthrough in autonomous agent design, providing authentic AI cognition that goes far beyond traditional rule-based systems. The combination of LLM reasoning, episodic memory, automatic reflection, and autonomous planning creates agents that truly think, remember, learn, and grow.

**Next**: Explore [Planning System](guides/planning-system.md) or [Memory System](guides/memory-system.md) for implementation details.
