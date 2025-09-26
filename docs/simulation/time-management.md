# Simulation Time Management

Technical documentation for the time management system that controls simulation progression, tick scheduling, and temporal coordination across all simulation components.

## ⏰ Overview

The Time Management system provides precise control over simulation progression through discrete time steps (ticks). It coordinates agent actions, world updates, and system events while maintaining consistent temporal relationships and enabling both real-time and accelerated simulation modes.

### Key Responsibilities

- **Tick Coordination**: Synchronize all simulation components on discrete time steps
- **Scheduling**: Manage agent processing order and timing
- **Temporal Consistency**: Ensure all events occur in proper temporal sequence
- **Performance Control**: Balance simulation speed with computational resources
- **State Synchronization**: Coordinate updates across memory, planning, and world systems

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────┐
│         Time Management System          │
├─────────────────────────────────────────┤
│  ⏱️ Simulation Controller                │
│     • Tick generation and dispatch      │
│     • Agent processing coordination     │
│     • Performance monitoring            │
├─────────────────────────────────────────┤
│  📅 Temporal Coordination              │
│     • Event sequencing                  │
│     • State synchronization             │
│     • Tick validation                   │
├─────────────────────────────────────────┤
│  🎯 Processing Pipeline                 │
│     • Agent tick processing             │
│     • World state updates               │
│     • Memory and planning updates       │
├─────────────────────────────────────────┤
│  📊 Performance Management              │
│     • Tick timing analysis              │
│     • Resource usage monitoring         │
│     • Adaptive scheduling               │
└─────────────────────────────────────────┘
```

### Core Files

- **`src/simulacra/simulation/simulation_controller.py`** - Main simulation coordination
- **`src/simulacra/models/simulation.py`** - Simulation state and tick models
- **`src/simulacra/logging/simulation_logger.py`** - Time-based logging and monitoring

## ⏱️ Simulation Controller

The Simulation Controller orchestrates all temporal aspects of the simulation.

### Core Architecture

```python
class SimulationController:
    def __init__(self, session_name: Optional[str] = None):
        self.session_name = session_name or f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.tick_count = 0
        self.start_time = None
        self.last_tick_time = None
        self.is_running = False
        self.is_paused = False
        
        # Performance tracking
        self.tick_durations = deque(maxlen=100)  # Last 100 tick times
        self.agent_processing_times = {}
        self.total_agents_processed = 0
        
        # Component coordination
        self.agents: Dict[str, Agent] = {}
        self.agent_processing_order = []
        self.next_agent_index = 0

    async def initialize(self) -> None:
        """Initialize simulation components and state."""
        
        # Initialize core components
        await self.storage.initialize()
        await self.world_manager.initialize("config/world.json")
        await self.memory_manager.initialize()
        
        # Load agents
        self.agents = await self._load_agents()
        self.agent_processing_order = list(self.agents.keys())
        
        # Initialize logging
        self.sim_logger.initialize_session(self.session_name)
        
        logger.info(f"Simulation initialized: {len(self.agents)} agents, session: {self.session_name}")
```

### Tick Processing Pipeline

```python
async def process_tick(self) -> TickResult:
    """Process a single simulation tick."""
    
    if not self.is_running or self.is_paused:
        return TickResult(success=False, message="Simulation not running")
    
    tick_start_time = time.time()
    self.tick_count += 1
    
    try:
        # Pre-tick validation
        await self._validate_simulation_state()
        
        # Process agents in round-robin fashion
        agents_processed = await self._process_agent_batch()
        
        # Update world state
        await self._update_world_state()
        
        # Handle tick completion
        await self._on_tick_complete()
        
        # Performance tracking
        tick_duration = time.time() - tick_start_time
        self.tick_durations.append(tick_duration)
        self.last_tick_time = datetime.now()
        
        # Logging
        self.sim_logger.log_tick_complete({
            "tick": self.tick_count,
            "agents_processed": agents_processed,
            "duration": tick_duration,
            "performance": self._get_performance_metrics()
        })
        
        return TickResult(
            success=True,
            tick_number=self.tick_count,
            agents_processed=agents_processed,
            duration=tick_duration
        )
        
    except Exception as e:
        logger.error(f"Error processing tick {self.tick_count}: {e}")
        return TickResult(
            success=False,
            tick_number=self.tick_count,
            error=str(e)
        )

async def _process_agent_batch(self) -> int:
    """Process a batch of agents for this tick."""
    
    # Determine how many agents to process this tick
    batch_size = self._calculate_optimal_batch_size()
    agents_processed = 0
    
    for _ in range(batch_size):
        if self.next_agent_index >= len(self.agent_processing_order):
            self.next_agent_index = 0  # Wrap around
        
        agent_id = self.agent_processing_order[self.next_agent_index]
        agent = self.agents.get(agent_id)
        
        if agent:
            await self._process_agent_tick(agent, self.tick_count)
            agents_processed += 1
        
        self.next_agent_index += 1
    
    self.total_agents_processed += agents_processed
    return agents_processed

def _calculate_optimal_batch_size(self) -> int:
    """Calculate optimal number of agents to process per tick."""
    
    total_agents = len(self.agents)
    
    # Target processing all agents over 5-10 ticks
    TARGET_CYCLE_TICKS = 7
    base_batch_size = max(1, total_agents // TARGET_CYCLE_TICKS)
    
    # Adjust based on recent performance
    if len(self.tick_durations) > 10:
        avg_tick_time = sum(self.tick_durations) / len(self.tick_durations)
        
        # If ticks are taking too long, reduce batch size
        if avg_tick_time > 2.0:  # More than 2 seconds per tick
            base_batch_size = max(1, base_batch_size // 2)
        # If ticks are very fast, increase batch size
        elif avg_tick_time < 0.5:  # Less than 0.5 seconds per tick
            base_batch_size = min(total_agents, base_batch_size * 2)
    
    return base_batch_size
```

### Agent Processing Coordination

```python
async def _process_agent_tick(self, agent: Agent, tick: int) -> None:
    """Process a single agent's tick with full cognitive pipeline."""
    
    agent_start_time = time.time()
    
    try:
        # Planning phase - check if agent should update their plan
        if await self.planning_engine.should_plan(agent):
            logger.info(f"Triggering daily planning for {agent.name}")
            daily_plan = await self.planning_engine.generate_daily_plan(agent)
            
            if daily_plan:
                plan_summary = self._create_plan_summary(daily_plan)
                self.sim_logger.log_agent_planning(agent.name, len(daily_plan.hourly_blocks), plan_summary)
        
        # Reflection phase - check if agent should reflect
        if await self.reflection_engine.should_reflect(agent):
            logger.info(f"Triggering reflection for {agent.name}")
            reflections = await self.reflection_engine.generate_reflections(agent)
            
            if reflections:
                self.sim_logger.log_agent_reflection(agent.name, len(reflections))
        
        # Decision and action phase
        action = await self.behavior_system.decide_action(agent)
        result = await self.behavior_system.execute_action(agent, action)
        
        # Memory formation
        await self._process_agent_memory_formation(agent, action, result)
        
        # Update agent state
        await self._update_agent_state(agent, action, result)
        
        # Performance tracking
        processing_time = time.time() - agent_start_time
        self.agent_processing_times[agent.id] = processing_time
        
        # Logging
        self.sim_logger.log_agent_action(
            agent_name=agent.name,
            action_type=action.action_type.value,
            reasoning=action.reasoning,
            result=result.description,
            success=result.success,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error processing agent {agent.name} on tick {tick}: {e}")
        self.sim_logger.log_agent_error(agent.name, str(e))

async def _process_agent_memory_formation(self, agent: Agent, action: Action, result: ActionResult) -> None:
    """Process memory formation for agent's action."""
    
    # Create action memory
    action_content = f"I performed {action.action_type.value}"
    if action.parameters:
        action_content += f" with parameters: {action.parameters}"
    action_content += f". {result.description}"
    
    await self.memory_manager.add_memory(
        agent_id=agent.id,
        content=action_content,
        memory_type=MemoryType.ACTION,
        metadata={"tick": self.tick_count, "success": result.success}
    )
    
    # Create observation memories if applicable
    if result.observation:
        await self.memory_manager.add_memory(
            agent_id=agent.id,
            content=f"I observed: {result.description}",
            memory_type=MemoryType.OBSERVATION,
            metadata={"tick": self.tick_count}
        )
```

## 📅 Temporal Coordination

### Event Sequencing

```python
class EventScheduler:
    """Manages scheduled events and temporal coordination."""
    
    def __init__(self):
        self.scheduled_events: List[ScheduledEvent] = []
        self.recurring_events: List[RecurringEvent] = []
        self.event_history: List[CompletedEvent] = []
    
    def schedule_event(self, event: ScheduledEvent) -> None:
        """Schedule a future event."""
        # Insert in chronological order
        insert_pos = 0
        for i, existing_event in enumerate(self.scheduled_events):
            if existing_event.scheduled_tick > event.scheduled_tick:
                break
            insert_pos = i + 1
        
        self.scheduled_events.insert(insert_pos, event)
        logger.info(f"Scheduled event {event.event_type} for tick {event.scheduled_tick}")
    
    def add_recurring_event(self, event: RecurringEvent) -> None:
        """Add a recurring event pattern."""
        self.recurring_events.append(event)
        
        # Schedule first occurrence
        next_tick = event.calculate_next_occurrence(0)
        if next_tick is not None:
            scheduled = ScheduledEvent(
                event_type=event.event_type,
                scheduled_tick=next_tick,
                parameters=event.parameters,
                recurring_id=event.id
            )
            self.schedule_event(scheduled)
    
    async def process_tick_events(self, current_tick: int) -> List[CompletedEvent]:
        """Process all events scheduled for current tick."""
        
        completed_events = []
        
        # Process scheduled events
        while (self.scheduled_events and 
               self.scheduled_events[0].scheduled_tick <= current_tick):
            
            event = self.scheduled_events.pop(0)
            
            try:
                result = await self._execute_event(event)
                completed_event = CompletedEvent(
                    event=event,
                    executed_tick=current_tick,
                    success=True,
                    result=result
                )
                completed_events.append(completed_event)
                
                # Handle recurring events
                if event.recurring_id:
                    await self._reschedule_recurring_event(event, current_tick)
                    
            except Exception as e:
                logger.error(f"Failed to execute event {event.event_type}: {e}")
                completed_event = CompletedEvent(
                    event=event,
                    executed_tick=current_tick,
                    success=False,
                    error=str(e)
                )
                completed_events.append(completed_event)
        
        # Store completed events
        self.event_history.extend(completed_events)
        
        return completed_events

class ScheduledEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    scheduled_tick: int
    parameters: Dict[str, Any] = Field(default_factory=dict)
    recurring_id: Optional[str] = None

class RecurringEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    recurrence_pattern: str  # "daily", "hourly", "weekly", etc.
    recurrence_interval: int = 1
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    def calculate_next_occurrence(self, from_tick: int) -> Optional[int]:
        """Calculate next occurrence of recurring event."""
        
        if self.recurrence_pattern == "hourly":
            # Every N simulation hours (assuming 1 tick = 5 minutes)
            ticks_per_hour = 12  # 60 minutes / 5 minutes per tick
            return from_tick + (ticks_per_hour * self.recurrence_interval)
        
        elif self.recurrence_pattern == "daily":
            # Every N simulation days (assuming 24 hours = 288 ticks)
            ticks_per_day = 288  # 24 * 12 ticks per hour
            return from_tick + (ticks_per_day * self.recurrence_interval)
        
        return None
```

### State Synchronization

```python
async def _validate_simulation_state(self) -> None:
    """Validate simulation state consistency before tick processing."""
    
    # Validate agent locations
    for agent_id, agent in self.agents.items():
        location = await self.world_manager.get_agent_location(agent_id)
        if not location:
            logger.warning(f"Agent {agent_id} has no location, assigning to default")
            await self.world_manager.move_agent(agent_id, "default_location")
    
    # Validate world state consistency
    await self.world_manager.validate_consistency()
    
    # Check for memory system health
    memory_stats = await self.memory_manager.get_system_stats()
    if memory_stats.error_count > 10:
        logger.warning(f"Memory system showing {memory_stats.error_count} errors")

async def _on_tick_complete(self) -> None:
    """Handle post-tick coordination and cleanup."""
    
    # Update simulation statistics
    await self._update_simulation_statistics()
    
    # Process any scheduled events
    completed_events = await self.event_scheduler.process_tick_events(self.tick_count)
    
    # Trigger periodic maintenance
    if self.tick_count % 100 == 0:  # Every 100 ticks
        await self._periodic_maintenance()
    
    # Memory cleanup for long-running simulations
    if self.tick_count % 1000 == 0:  # Every 1000 ticks
        await self._memory_cleanup()

async def _periodic_maintenance(self) -> None:
    """Perform periodic system maintenance."""
    
    # Clean up old temporary data
    await self.storage.cleanup_old_temporary_data()
    
    # Optimize database if needed
    if self.tick_count % 5000 == 0:  # Every 5000 ticks
        await self.storage.optimize_database()
    
    # Update agent energy levels (simulate rest/recovery)
    for agent in self.agents.values():
        if agent.energy < 100:
            # Slow energy recovery over time
            agent.energy = min(100, agent.energy + 1)
            await self.storage.update_agent(agent)
```

## 🎯 Processing Pipeline

### Pipeline Architecture

```python
class TickProcessingPipeline:
    """Manages the ordered processing pipeline for each tick."""
    
    def __init__(self, simulation_controller):
        self.controller = simulation_controller
        self.pipeline_stages = [
            self._stage_pre_processing,
            self._stage_agent_cognition,
            self._stage_agent_actions,
            self._stage_world_updates,
            self._stage_post_processing
        ]
    
    async def execute_pipeline(self, tick_number: int) -> TickResult:
        """Execute the complete tick processing pipeline."""
        
        stage_results = {}
        
        for i, stage in enumerate(self.pipeline_stages):
            stage_name = stage.__name__
            stage_start = time.time()
            
            try:
                stage_result = await stage(tick_number)
                stage_duration = time.time() - stage_start
                
                stage_results[stage_name] = {
                    "success": True,
                    "duration": stage_duration,
                    "result": stage_result
                }
                
            except Exception as e:
                stage_duration = time.time() - stage_start
                stage_results[stage_name] = {
                    "success": False,
                    "duration": stage_duration,
                    "error": str(e)
                }
                
                # Decide whether to continue or abort pipeline
                if self._is_critical_stage_failure(stage_name, e):
                    logger.error(f"Critical failure in {stage_name}, aborting tick")
                    break
                else:
                    logger.warning(f"Non-critical failure in {stage_name}, continuing")
        
        return TickResult(
            success=all(result["success"] for result in stage_results.values()),
            tick_number=tick_number,
            stage_results=stage_results,
            total_duration=sum(result["duration"] for result in stage_results.values())
        )
    
    async def _stage_pre_processing(self, tick_number: int) -> Dict[str, Any]:
        """Pre-processing stage: validation and setup."""
        
        # Validate simulation state
        await self.controller._validate_simulation_state()
        
        # Prepare agent processing order
        self.controller._shuffle_agent_processing_order()
        
        # Check system resources
        system_stats = await self.controller._get_system_resource_stats()
        
        return {
            "agents_ready": len(self.controller.agents),
            "system_stats": system_stats
        }
    
    async def _stage_agent_cognition(self, tick_number: int) -> Dict[str, Any]:
        """Agent cognition stage: planning and reflection."""
        
        cognition_results = {
            "plans_generated": 0,
            "reflections_generated": 0,
            "agents_processed": 0
        }
        
        # Process a subset of agents for cognition this tick
        agents_to_process = self.controller._get_agents_for_cognition_tick()
        
        for agent in agents_to_process:
            # Planning
            if await self.controller.planning_engine.should_plan(agent):
                plan = await self.controller.planning_engine.generate_daily_plan(agent)
                if plan:
                    cognition_results["plans_generated"] += 1
            
            # Reflection
            if await self.controller.reflection_engine.should_reflect(agent):
                reflections = await self.controller.reflection_engine.generate_reflections(agent)
                if reflections:
                    cognition_results["reflections_generated"] += 1
            
            cognition_results["agents_processed"] += 1
        
        return cognition_results
    
    async def _stage_agent_actions(self, tick_number: int) -> Dict[str, Any]:
        """Agent action stage: decision making and action execution."""
        
        action_results = {
            "actions_executed": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "agents_processed": 0
        }
        
        # Process agents for actions
        agents_to_process = self.controller._get_agents_for_action_tick()
        
        for agent in agents_to_process:
            try:
                # Decide and execute action
                action = await self.controller.behavior_system.decide_action(agent)
                result = await self.controller.behavior_system.execute_action(agent, action)
                
                action_results["actions_executed"] += 1
                if result.success:
                    action_results["successful_actions"] += 1
                else:
                    action_results["failed_actions"] += 1
                
                # Form memories
                await self.controller._process_agent_memory_formation(agent, action, result)
                
            except Exception as e:
                logger.error(f"Failed to process actions for {agent.name}: {e}")
                action_results["failed_actions"] += 1
            
            action_results["agents_processed"] += 1
        
        return action_results
```

## 📊 Performance Management

### Performance Monitoring

```python
class PerformanceMonitor:
    """Monitors and analyzes simulation performance."""
    
    def __init__(self):
        self.tick_metrics = deque(maxlen=1000)
        self.agent_metrics = {}
        self.system_metrics = {}
        self.bottleneck_analysis = []
    
    def record_tick_performance(self, tick_result: TickResult) -> None:
        """Record performance metrics for a completed tick."""
        
        metrics = TickPerformanceMetrics(
            tick_number=tick_result.tick_number,
            total_duration=tick_result.total_duration,
            agents_processed=tick_result.agents_processed,
            success=tick_result.success,
            timestamp=datetime.now()
        )
        
        if tick_result.stage_results:
            metrics.stage_durations = {
                stage: result["duration"] 
                for stage, result in tick_result.stage_results.items()
            }
        
        self.tick_metrics.append(metrics)
        
        # Analyze for bottlenecks
        self._analyze_bottlenecks(metrics)
    
    def get_performance_summary(self, window_size: int = 100) -> PerformanceSummary:
        """Get performance summary over recent ticks."""
        
        recent_metrics = list(self.tick_metrics)[-window_size:]
        
        if not recent_metrics:
            return PerformanceSummary()
        
        total_duration = sum(m.total_duration for m in recent_metrics)
        successful_ticks = sum(1 for m in recent_metrics if m.success)
        
        return PerformanceSummary(
            window_size=len(recent_metrics),
            average_tick_duration=total_duration / len(recent_metrics),
            success_rate=successful_ticks / len(recent_metrics),
            total_agents_processed=sum(m.agents_processed for m in recent_metrics),
            bottlenecks=self._identify_current_bottlenecks(),
            recommendations=self._generate_performance_recommendations()
        )
    
    def _analyze_bottlenecks(self, metrics: TickPerformanceMetrics) -> None:
        """Analyze individual tick for performance bottlenecks."""
        
        if metrics.stage_durations:
            # Find slowest stage
            slowest_stage = max(metrics.stage_durations.items(), key=lambda x: x[1])
            
            if slowest_stage[1] > 2.0:  # More than 2 seconds
                bottleneck = PerformanceBottleneck(
                    type="stage_slowdown",
                    component=slowest_stage[0],
                    severity=slowest_stage[1],
                    tick_number=metrics.tick_number,
                    timestamp=metrics.timestamp
                )
                self.bottleneck_analysis.append(bottleneck)
    
    def _generate_performance_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations."""
        
        recommendations = []
        recent_metrics = list(self.tick_metrics)[-50:]  # Last 50 ticks
        
        if recent_metrics:
            avg_duration = sum(m.total_duration for m in recent_metrics) / len(recent_metrics)
            
            if avg_duration > 3.0:
                recommendations.append("Consider reducing agent batch size for faster ticks")
            
            if avg_duration < 0.2:
                recommendations.append("Consider increasing agent batch size for better throughput")
            
            # Analyze stage performance
            stage_times = defaultdict(list)
            for metrics in recent_metrics:
                if metrics.stage_durations:
                    for stage, duration in metrics.stage_durations.items():
                        stage_times[stage].append(duration)
            
            for stage, durations in stage_times.items():
                avg_stage_time = sum(durations) / len(durations)
                if avg_stage_time > 1.0:
                    recommendations.append(f"Optimize {stage} stage - averaging {avg_stage_time:.2f}s")
        
        return recommendations

class TickPerformanceMetrics(BaseModel):
    tick_number: int
    total_duration: float
    agents_processed: int
    success: bool
    timestamp: datetime
    stage_durations: Dict[str, float] = Field(default_factory=dict)

class PerformanceSummary(BaseModel):
    window_size: int = 0
    average_tick_duration: float = 0.0
    success_rate: float = 0.0
    total_agents_processed: int = 0
    bottlenecks: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
```

### Adaptive Scheduling

```python
class AdaptiveScheduler:
    """Dynamically adjusts simulation parameters based on performance."""
    
    def __init__(self, performance_monitor: PerformanceMonitor):
        self.performance_monitor = performance_monitor
        self.adaptive_parameters = {
            "agent_batch_size": 3,
            "tick_target_duration": 1.0,  # Target 1 second per tick
            "memory_cleanup_interval": 1000,
            "reflection_frequency": 0.1  # 10% chance per agent per tick
        }
        self.adjustment_history = []
    
    async def adjust_parameters(self) -> None:
        """Adjust simulation parameters based on recent performance."""
        
        summary = self.performance_monitor.get_performance_summary(window_size=50)
        
        if summary.window_size < 10:
            return  # Not enough data
        
        adjustments_made = []
        
        # Adjust batch size based on tick duration
        if summary.average_tick_duration > self.adaptive_parameters["tick_target_duration"] * 1.5:
            # Ticks too slow, reduce batch size
            old_batch_size = self.adaptive_parameters["agent_batch_size"]
            self.adaptive_parameters["agent_batch_size"] = max(1, old_batch_size - 1)
            adjustments_made.append(f"Reduced batch size: {old_batch_size} -> {self.adaptive_parameters['agent_batch_size']}")
        
        elif summary.average_tick_duration < self.adaptive_parameters["tick_target_duration"] * 0.5:
            # Ticks too fast, increase batch size
            old_batch_size = self.adaptive_parameters["agent_batch_size"]
            self.adaptive_parameters["agent_batch_size"] = min(10, old_batch_size + 1)
            adjustments_made.append(f"Increased batch size: {old_batch_size} -> {self.adaptive_parameters['agent_batch_size']}")
        
        # Adjust reflection frequency based on performance
        if "reflection" in summary.bottlenecks:
            old_frequency = self.adaptive_parameters["reflection_frequency"]
            self.adaptive_parameters["reflection_frequency"] = max(0.01, old_frequency * 0.8)
            adjustments_made.append(f"Reduced reflection frequency: {old_frequency:.2f} -> {self.adaptive_parameters['reflection_frequency']:.2f}")
        
        # Record adjustments
        if adjustments_made:
            adjustment_record = AdaptiveAdjustment(
                timestamp=datetime.now(),
                adjustments=adjustments_made,
                trigger_metrics=summary
            )
            self.adjustment_history.append(adjustment_record)
            logger.info(f"Adaptive scheduling adjustments: {adjustments_made}")

class AdaptiveAdjustment(BaseModel):
    timestamp: datetime
    adjustments: List[str]
    trigger_metrics: PerformanceSummary
```

## 🎯 Future Enhancements

### Planned Features

1. **Parallel Processing**: Multi-threaded agent processing for large simulations
2. **Dynamic Time Scaling**: Variable time step sizes based on activity levels
3. **Event-Driven Scheduling**: Interrupt-based processing for high-priority events
4. **Distributed Simulation**: Multi-node simulation for massive scale
5. **Real-Time Synchronization**: Wall-clock time synchronization options

### Research Directions

- Optimal tick scheduling algorithms for different simulation scales
- Predictive performance modeling and proactive optimization
- Temporal consistency validation across distributed components
- Energy-efficient simulation scheduling for battery-powered devices
- Adaptive load balancing for heterogeneous agent populations

---

The Time Management system ensures smooth, consistent, and efficient simulation progression while providing the flexibility to adapt to different performance requirements and scales.
