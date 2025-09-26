# CLI Reference

Complete command-line interface reference for the AI Simulacra Agents system. The CLI provides full control over agent simulation, cognitive inspection, and system management.

## 🚀 Quick Reference

| Command | Description | Example |
|---------|-------------|---------|
| [`step`](#step) | Run one simulation step | `python main.py step` |
| [`start`](#start) | Start continuous simulation | `python main.py start` |
| [`agent`](#agent) | Inspect agent details | `python main.py agent isabella` |
| [`plan`](#plan) | View/generate agent plans | `python main.py plan isabella` |
| [`reflect`](#reflect) | Trigger agent reflection | `python main.py reflect isabella` |
| [`status`](#status) | Show simulation status | `python main.py status` |
| [`export`](#export) | Export simulation data | `python main.py export` |
| [`interactive`](#interactive) | Interactive mode | `python main.py interactive` |

## 📊 Simulation Commands

### `step`
Run a single simulation step (tick) and watch agents think, plan, and act.

```bash
python main.py step
```

**What happens**:
1. **Time advances** by one tick (5 minutes simulation time)
2. **Each agent processes** in sequence:
   - Memory retrieval for decision context
   - LLM-powered decision making with reasoning
   - Action execution with beautiful visualization
   - Memory formation and importance scoring
   - Automatic reflection if threshold reached
   - Automatic planning if triggers detected
3. **Agent status summary** displayed with planning information

**Example Output**:
```
╭─────────────────────────── 🤔 Isabella Rodriguez ────────────────────────────╮
│  🧠 Isabella Rodriguez is thinking...                                        │
│  📍 Currently at: Isabella's Apartment                                       │
│  💭 Reasoning: I'm feeling a bit down today, my mood is only 5.0 out of 10,  │
│  and I think it's because I haven't had much social interaction lately...    │
│  ✨ Decision: move to Community Cafe                                         │
╰──────────────────────────────────────────────────────────────────────────────╯

📊 Agent Status:
 Isabella Rodriguez  Community Cafe   ██████████ 100%  📋 Planning         
 John Kim            Main Street      ██████████ 100%  📋 Planning         
 Maria Santos        Main Street      ██████████ 100%  📋 Planning         
```

### `start`
Start continuous simulation that runs automatically until interrupted.

```bash
python main.py start
```

**Options**:
- `--ticks N` - Run for N ticks then stop
- `--delay SECONDS` - Delay between ticks (default: 2.0)

**Examples**:
```bash
python main.py start --ticks 10        # Run 10 ticks then stop
python main.py start --delay 1.0       # Faster execution (1 second delay)
python main.py start --ticks 5 --delay 0.5  # 5 quick ticks
```

**Controls**:
- `Ctrl+C` - Stop simulation gracefully
- Automatic export on completion

## 🤖 Agent Inspection Commands

### `agent`
Inspect detailed agent information including cognition, memory, and planning.

```bash
python main.py agent <agent_id> [options]
```

**Required Arguments**:
- `agent_id` - Agent identifier (`isabella`, `john`, `maria`)

**Options**:
- `--memories N` - Show N recent memories (default: 10)
- `--query TEXT` - Search memories with semantic query
- `--reflections` - Show agent reflections instead of memories

**Examples**:

**Basic agent inspection**:
```bash
python main.py agent isabella
```

**View specific number of memories**:
```bash
python main.py agent isabella --memories 20
```

**Search memories semantically**:
```bash
python main.py agent isabella --query "social interaction"
python main.py agent john --query "work and creativity"
python main.py agent maria --query "community activities"
```

**View agent reflections**:
```bash
python main.py agent isabella --reflections
```

**Output Sections**:
1. **Agent Profile** - Name, bio, personality, home location
2. **Current State** - Location, energy, mood, status, reflection progress
3. **Planning Information** - Current goals, tasks, plan status
4. **Memory Display** - Recent memories or search results with importance scores
5. **Available Actions** - What the agent can currently do

**Example Output**:
```
╭───────────────────────── Agent: Isabella Rodriguez ──────────────────────────╮
│ ID: isabella                                                                 │
│ Bio: Isabella is a warm and community-minded cafe owner who loves hosting    │
│ events and bringing people together...                                       │
│ Personality: warm, community-minded, creative, empathetic, organized         │
│ Home: apartment_1                                                            │
╰──────────────────────────────────────────────────────────────────────────────╯

╭─────────────────────────────── Current State ────────────────────────────────╮
│ Location: Community Cafe                                                     │
│ Status: active                                                               │
│ Energy: 95.5/100                                                             │
│ Mood: 7.2/10                                                                 │
│ Reflection Progress: 12.5/15.0 (83%)                                         │
╰──────────────────────────────────────────────────────────────────────────────╯

╭───────────────────────────── 📅 Daily Planning ──────────────────────────────╮
│ 📋 HAS DAILY PLAN                                                            │
│ 🎯 Goal: Take a moment to recharge and connect with my community             │
│ 📌 Current Task: Practice yoga and meditation in the cafe's peaceful atmosphere │
│ ⏰ Plan has 2 time blocks                                                    │
╰──────────────────────────────────────────────────────────────────────────────╯

Recent memories for isabella:
1. I moved from apartment_1 to cafe. Moved from apartment_1 to Community Cafe 
   (importance: 6.5, action) [14:32]
2. I observed my surroundings at Community Cafe. Observed surroundings: At 
   Community Cafe: A cozy neighborhood cafe... (importance: 4.0, action) [14:31]
```

### `plan`
View or generate agent daily plans with beautiful formatting.

```bash
python main.py plan <agent_id> [options]
```

**Required Arguments**:
- `agent_id` - Agent identifier

**Options**:
- `--generate` - Force generation of a new daily plan

**Examples**:

**View current plan**:
```bash
python main.py plan isabella
```

**Generate new plan**:
```bash
python main.py plan isabella --generate
```

**Output**:
```
╭───────────────────── 🗓️ Isabella Rodriguez's Daily Plan ─────────────────────╮
│ 📅 Daily Plan for 2025-09-26                                                │
│                                                                              │
│ 🎯 Goals for Today:                                                         │
│   1. To take a moment for self-care, recharge, and connect with my          │
│   community by hosting an intimate gathering at the cafe.                   │
│                                                                              │
│ 📋 Schedule:                                                                │
│   ✅ 09:00 - 12:00 - Take some time for self-care by practicing yoga and    │
│   meditation in the cafe's peaceful atmosphere. (at Cafe (quiet corner))    │
│     📌 Take some time for self-care by practicing yoga and meditation in    │
│   the cafe's peaceful atmosphere.                                           │
│                                                                              │
│   ⏳ 13:00 - 17:00 - Host an informal community gathering to bring people   │
│   together. (at Community Cafe (main area))                                 │
│     📌 Set up welcoming space for community gathering                       │
│     📌 Engage with visitors and facilitate conversations                    │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### `reflect`
Manually trigger reflection for an agent to generate new insights.

```bash
python main.py reflect <agent_id>
```

**What happens**:
1. **Gathers recent memories** (typically 15-20 most recent)
2. **Filters high-importance experiences** (importance ≥ 6.0)
3. **LLM analyzes patterns** in agent behavior and experiences
4. **Generates 3-5 insights** about the agent's psychology and patterns
5. **Stores reflections** as high-importance memories (8.0)
6. **Beautiful display** of generated insights

**Example**:
```bash
python main.py reflect maria
```

**Output**:
```
╭────────────────────────────── 💡 Maria Santos ───────────────────────────────╮
│  🧠 REFLECTION GENERATED                                                     │
│  💭 Generated 3 new insights:                                                │
│                                                                              │
│  1. **Maria is seeking balance between independence and community**: Her     │
│  frequent moves between private apartment and public spaces suggest she      │
│  values both solitude for reflection and community engagement for fulfillment │
│                                                                              │
│  2. **Maria finds meaning in nurturing growth**: Whether tending to plants   │
│  in the garden or engaging in community activities, she is drawn to activities │
│  that foster development and positive change in her environment.             │
│                                                                              │
│  3. **Maria values stability through routine**: Her consistent patterns of   │
│  movement and activity suggest she finds comfort in predictable rhythms while │
│  remaining open to meaningful interactions and experiences.                  │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## 📊 System Status Commands

### `status`
Display comprehensive system and world state information.

```bash
python main.py status
```

**Output Sections**:
1. **Simulation Overview** - Current tick, elapsed time, total agents
2. **Agent Locations** - Where each agent is currently located
3. **Place Occupancy** - Which agents are at each location
4. **System Health** - Database stats, memory usage

**Example Output**:
```
╭──────────────────────────────────────────────────────────────────────────────╮
│ Simulation Status: ACTIVE                                                    │
╰──────────────────────────────────────────────────────────────────────────────╯

⏰ Tick: 15 (75 minutes elapsed)
🌍 World: 7 places, 3 agents

                     Agent Locations                     
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┓
┃ Agent              ┃ Location       ┃ Energy ┃ Status ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━┩
│ Isabella Rodriguez │ Community Cafe │ 95.5   │ active │
│ John Kim           │ John's Home    │ 87.2   │ active │
│ Maria Santos       │ Community Garden│ 92.8   │ active │
└────────────────────┴────────────────┴────────┴────────┘

📍 Place Occupancy:
  • Community Cafe: 1 agents (isabella)
  • John's Home: 1 agents (john)
  • Community Garden: 1 agents (maria)
  • Main Street: 0 agents
```

### `export`
Export simulation data for analysis and research.

```bash
python main.py export [options]
```

**Options**:
- `--format FORMAT` - Export format: `csv`, `json`, or `all` (default: all)
- `--session SESSION` - Export specific session (default: current)

**Examples**:
```bash
python main.py export                    # Export all current data
python main.py export --format csv       # CSV files only
python main.py export --format json      # JSON files only
python main.py export --session sim_20250926_143444  # Specific session
```

**Generated Files**:
- `agent_actions.csv` - All agent actions with timestamps and reasoning
- `simulation_state.csv` - Agent states at each tick
- `movement_analysis.csv` - Location changes and movement patterns
- `social_analysis.csv` - Agent interaction patterns
- `vitals_analysis.csv` - Energy, mood, and status tracking
- `timeseries_analysis.csv` - Time-series data for analysis
- `complete_simulation.json` - Full simulation data in JSON format
- `summary_report.md` - Human-readable simulation summary

## 🎮 Interactive Commands

### `interactive`
Start interactive mode for real-time simulation control.

```bash
python main.py interactive
```

**Interactive Commands**:
- `step` - Run one simulation step
- `agent <id>` - Inspect agent
- `plan <id>` - View agent plan
- `reflect <id>` - Trigger reflection
- `status` - Show system status
- `export` - Export data
- `help` - Show available commands
- `quit` - Exit interactive mode

**Example Session**:
```
🤖 AI Simulacra Agents - Interactive Mode
Type 'help' for commands, 'quit' to exit

> step
[Beautiful simulation step output]

> agent isabella
[Agent inspection output]

> plan isabella --generate
[Plan generation output]

> quit
Goodbye!
```

## ⚙️ Global Options

### Common Flags

**Verbose Output**:
```bash
python main.py --verbose step    # More detailed logging
python main.py -v agent john     # Short form
```

**Quiet Mode**:
```bash
python main.py --quiet step      # Minimal output
python main.py -q status         # Short form
```

**Configuration**:
```bash
python main.py --config custom_config.json step    # Custom config file
```

**Help**:
```bash
python main.py --help            # General help
python main.py agent --help      # Command-specific help
```

## 🔧 Advanced Usage

### Batch Operations

**Multiple Agents**:
```bash
# Inspect all agents
for agent in isabella john maria; do
    python main.py agent $agent --memories 5
done

# Generate plans for all agents
for agent in isabella john maria; do
    python main.py plan $agent --generate
done
```

**Automated Analysis**:
```bash
# Run simulation and export
python main.py start --ticks 20
python main.py export --format csv

# Analyze specific agent behavior
python main.py agent isabella --query "social interaction" > isabella_social.txt
python main.py agent john --query "creative work" > john_creative.txt
```

### Research Workflows

**Cognitive Study Session**:
```bash
# 1. Baseline inspection
python main.py agent isabella --memories 20 > baseline_isabella.txt

# 2. Run controlled simulation
python main.py start --ticks 10 --delay 1.0

# 3. Post-simulation analysis
python main.py agent isabella --reflections > reflections_isabella.txt
python main.py plan isabella > plan_isabella.txt

# 4. Export for analysis
python main.py export --format all
```

**Memory Formation Study**:
```bash
# Track memory formation over multiple steps
for i in {1..5}; do
    echo "=== Step $i ===" >> memory_study.txt
    python main.py step
    python main.py agent isabella --memories 3 >> memory_study.txt
done
```

## 🚨 Error Handling

### Common Issues

**Agent Not Found**:
```bash
> python main.py agent unknown_agent
Error: Agent 'unknown_agent' not found
Available agents: isabella, john, maria
```

**No Current Plan**:
```bash
> python main.py plan john
No daily plan found for John Kim
Use --generate to create a new plan
```

**Database Issues**:
```bash
> python main.py step
Error: Database not initialized
Run: python scripts/init_db.py
```

### Exit Codes

- `0` - Success
- `1` - General error
- `2` - Invalid arguments
- `3` - Database error
- `4` - LLM service error

## 🎯 Best Practices

### Effective Agent Inspection

**Start Broad, Go Specific**:
```bash
# 1. General overview
python main.py agent isabella

# 2. Current planning status
python main.py plan isabella

# 3. Specific memory search
python main.py agent isabella --query "recent social interactions"

# 4. Reflection analysis
python main.py agent isabella --reflections
```

### Simulation Management

**Regular Exports**:
```bash
# Export after major simulation sessions
python main.py start --ticks 20
python main.py export
```

**Monitor Agent States**:
```bash
# Check system health periodically
python main.py status
```

### Research Data Collection

**Systematic Documentation**:
```bash
# Create timestamped exports
timestamp=$(date +%Y%m%d_%H%M%S)
python main.py export
cp -r output/latest_session output/study_${timestamp}
```

---

This CLI provides complete control over the AI agent simulation system. The beautiful terminal interfaces make it easy to observe authentic AI cognition in real-time, while the export capabilities enable comprehensive research and analysis.

**Next**: Explore [Agent Configuration](../guides/agent-configuration.md) or [Cognitive Architecture](../cognitive-architecture.md).
