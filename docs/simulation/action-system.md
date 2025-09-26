# Simulation Action System

Technical documentation for the action execution system that translates agent decisions into world state changes and manages the consequences of agent behaviors.

## 🎬 Overview

The Action System serves as the bridge between agent cognition and world state, executing agent decisions and managing their effects on the simulation environment. It handles action validation, execution, state updates, and consequence propagation while maintaining system consistency and performance.

### Key Responsibilities

- **Action Validation**: Ensure actions are legal and executable in current context
- **Execution Management**: Coordinate action effects across world, memory, and agent systems
- **State Consistency**: Maintain coherent world state during concurrent operations
- **Effect Propagation**: Handle cascading effects of actions on other agents and objects
- **Performance**: Execute actions efficiently even with complex interdependencies

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────┐
│            Action System                │
├─────────────────────────────────────────┤
│  🎯 Action Executor                     │
│     • Action validation                 │
│     • Execution coordination            │
│     • Effect management                 │
├─────────────────────────────────────────┤
│  🔄 Action Pipeline                     │
│     • Pre-execution validation          │
│     • Atomic execution                  │
│     • Post-execution cleanup            │
├─────────────────────────────────────────┤
│  📊 Effect Management                   │
│     • State change tracking             │
│     • Consequence propagation           │
│     • Rollback capabilities             │
├─────────────────────────────────────────┤
│  🛡️ Concurrency Control                │
│     • Action ordering                   │
│     • Conflict resolution               │
│     • Atomic operations                 │
└─────────────────────────────────────────┘
```

### Core Files

- **`src/simulacra/simulation/action_executor.py`** - Action execution coordination
- **`src/simulacra/models/action.py`** - Action definitions and results
- **`src/simulacra/simulation/llm_behavior.py`** - Action decision making integration

## 🎯 Action Executor

The Action Executor coordinates the execution of agent actions with full effect management.

### Core Architecture

```python
class ActionExecutor:
    def __init__(
        self,
        world_manager: WorldManager,
        memory_manager: MemoryManager,
        storage: SQLiteStore
    ):
        self.world_manager = world_manager
        self.memory_manager = memory_manager
        self.storage = storage
        
        # Execution tracking
        self.active_actions: Dict[str, Action] = {}
        self.action_history: List[CompletedAction] = []
        self.execution_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        
        # Performance metrics
        self.execution_times: Dict[ActionType, List[float]] = defaultdict(list)
        self.success_rates: Dict[ActionType, float] = {}

    async def execute_action(self, agent: Agent, action: Action) -> ActionResult:
        """Execute an action with full validation and effect management."""
        
        execution_id = f"{agent.id}_{action.action_type.value}_{int(time.time() * 1000)}"
        execution_start = time.time()
        
        try:
            # Pre-execution validation
            validation_result = await self._validate_action(agent, action)
            if not validation_result.valid:
                return ActionResult(
                    success=False,
                    description=validation_result.reason,
                    energy_cost=0,
                    execution_id=execution_id
                )
            
            # Execute action with appropriate handler
            async with self.execution_locks[agent.id]:  # Prevent concurrent actions for same agent
                self.active_actions[execution_id] = action
                
                result = await self._execute_action_by_type(agent, action)
                
                # Post-execution processing
                await self._process_action_effects(agent, action, result)
                
                del self.active_actions[execution_id]
            
            # Record performance metrics
            execution_time = time.time() - execution_start
            self.execution_times[action.action_type].append(execution_time)
            
            # Store action history
            completed_action = CompletedAction(
                action=action,
                result=result,
                agent_id=agent.id,
                execution_time=execution_time,
                timestamp=datetime.now()
            )
            self.action_history.append(completed_action)
            
            return result
            
        except Exception as e:
            logger.error(f"Action execution failed for {agent.name}: {e}")
            
            # Cleanup on failure
            if execution_id in self.active_actions:
                del self.active_actions[execution_id]
            
            return ActionResult(
                success=False,
                description=f"Execution error: {str(e)}",
                energy_cost=1,  # Small penalty for failed actions
                execution_id=execution_id
            )

    async def _validate_action(self, agent: Agent, action: Action) -> ActionValidationResult:
        """Comprehensive action validation."""
        
        # Check agent energy
        required_energy = self._get_action_energy_cost(action.action_type)
        if agent.energy < required_energy:
            return ActionValidationResult(
                valid=False,
                reason=f"Insufficient energy: {agent.energy} < {required_energy}"
            )
        
        # Validate action-specific requirements
        if action.action_type == ActionType.MOVE:
            return await self._validate_move_action(agent, action)
        elif action.action_type == ActionType.INTERACT:
            return await self._validate_interact_action(agent, action)
        elif action.action_type == ActionType.OBSERVE:
            return await self._validate_observe_action(agent, action)
        elif action.action_type == ActionType.WAIT:
            return ActionValidationResult(valid=True)  # Wait is always valid
        
        return ActionValidationResult(
            valid=False,
            reason=f"Unknown action type: {action.action_type}"
        )

class ActionValidationResult(BaseModel):
    valid: bool
    reason: str = ""
    suggested_alternative: Optional[Action] = None
```

### Action Type Handlers

```python
async def _execute_action_by_type(self, agent: Agent, action: Action) -> ActionResult:
    """Route action to appropriate execution handler."""
    
    if action.action_type == ActionType.MOVE:
        return await self._execute_move_action(agent, action)
    elif action.action_type == ActionType.INTERACT:
        return await self._execute_interact_action(agent, action)
    elif action.action_type == ActionType.OBSERVE:
        return await self._execute_observe_action(agent, action)
    elif action.action_type == ActionType.WAIT:
        return await self._execute_wait_action(agent, action)
    else:
        raise ValueError(f"Unsupported action type: {action.action_type}")

async def _execute_move_action(self, agent: Agent, action: Action) -> ActionResult:
    """Execute agent movement with full effect handling."""
    
    target_location = action.parameters.get("target_location")
    if not target_location:
        return ActionResult(
            success=False,
            description="Move action missing target_location parameter",
            energy_cost=1
        )
    
    # Get current location for context
    current_location = await self.world_manager.get_agent_location(agent.id)
    current_name = current_location.name if current_location else "unknown"
    
    # Attempt movement
    move_success = await self.world_manager.move_agent(agent.id, target_location)
    
    if move_success:
        # Get new location for result
        new_location = await self.world_manager.get_location(target_location)
        new_name = new_location.name if new_location else target_location
        
        # Check for other agents at destination
        other_agents = await self.world_manager.get_agents_at_location(target_location)
        other_agents = [a for a in other_agents if a.id != agent.id]
        
        description = f"Moved from {current_name} to {new_name}"
        if other_agents:
            other_names = [a.name for a in other_agents]
            description += f". Found {', '.join(other_names)} here"
        
        return ActionResult(
            success=True,
            description=description,
            energy_cost=5,
            location_change=True,
            new_location=target_location,
            agents_encountered=other_agents
        )
    else:
        return ActionResult(
            success=False,
            description=f"Cannot move to {target_location}",
            energy_cost=2  # Failed movement still costs some energy
        )

async def _execute_interact_action(self, agent: Agent, action: Action) -> ActionResult:
    """Execute social interaction with comprehensive effect handling."""
    
    target_agent_name = action.parameters.get("target_agent")
    if not target_agent_name:
        return ActionResult(
            success=False,
            description="Interact action missing target_agent parameter",
            energy_cost=1
        )
    
    # Find target agent
    current_location = await self.world_manager.get_agent_location(agent.id)
    nearby_agents = await self.world_manager.get_agents_at_location(current_location.id)
    
    target_agent = None
    for nearby_agent in nearby_agents:
        if nearby_agent.name.lower() == target_agent_name.lower() and nearby_agent.id != agent.id:
            target_agent = nearby_agent
            break
    
    if not target_agent:
        return ActionResult(
            success=False,
            description=f"Cannot find {target_agent_name} at {current_location.name}",
            energy_cost=2
        )
    
    # Generate interaction content using LLM
    interaction_result = await self._generate_social_interaction(
        agent, target_agent, current_location
    )
    
    # Create memories for both agents
    await self._create_interaction_memories(
        agent, target_agent, current_location, interaction_result
    )
    
    # Update social relationships if applicable
    await self._update_social_relationships(agent, target_agent, interaction_result)
    
    return ActionResult(
        success=True,
        description=f"Interacted with {target_agent.name}: {interaction_result.description}",
        energy_cost=3,
        social_interaction=True,
        interaction_target=target_agent.id,
        interaction_details=interaction_result.details
    )

async def _generate_social_interaction(
    self,
    agent: Agent,
    target_agent: Agent,
    location: Location
) -> InteractionResult:
    """Generate realistic social interaction using LLM."""
    
    # Build context for interaction
    context = {
        "initiator": agent,
        "target": target_agent,
        "location": location,
        "relationship": await self._get_relationship_context(agent, target_agent)
    }
    
    # Generate interaction using LLM
    interaction_prompt = f"""Generate a realistic social interaction between {agent.name} and {target_agent.name}.

Setting: {location.name} - {location.description}

{agent.name} (initiating):
- Personality: {agent.personality}
- Current mood: {agent.mood}/10
- Current energy: {agent.energy}/100

{target_agent.name} (responding):
- Personality: {target_agent.personality}
- Current mood: {target_agent.mood}/10

Relationship context: {context['relationship']}

Generate a brief but meaningful interaction (2-3 exchanges) that reflects their personalities and current states.
Focus on what they would naturally discuss and how they would interact.

Format:
INTERACTION: [Brief description of the interaction]
DETAILS: [Key points discussed or activities shared]
MOOD_EFFECT: [How this affects both agents' moods: positive/neutral/negative]"""
    
    response = await self.llm_service.generate_text(interaction_prompt)
    
    return self._parse_interaction_response(response)

async def _execute_observe_action(self, agent: Agent, action: Action) -> ActionResult:
    """Execute environmental observation with detailed perception."""
    
    location = await self.world_manager.get_agent_location(agent.id)
    nearby_agents = await self.world_manager.get_agents_at_location(location.id)
    nearby_agents = [a for a in nearby_agents if a.id != agent.id]
    
    # Get objects at location
    location_objects = await self.world_manager.get_objects_at_location(location.id)
    
    # Generate detailed observation using LLM
    observation_prompt = f"""You are {agent.name} carefully observing your environment.

Location: {location.name} - {location.description}
Your mood: {agent.mood}/10
Your energy: {agent.energy}/100

People present: {', '.join(a.name for a in nearby_agents) if nearby_agents else 'None'}
Objects visible: {', '.join(obj.name for obj in location_objects) if location_objects else 'None'}

Given your personality ({agent.personality}) and current state, what do you notice? 
What catches your attention? What details stand out to you?

Provide a vivid but concise observation that reflects your character's perspective."""
    
    observation_text = await self.llm_service.generate_text(observation_prompt)
    
    # Score observation importance
    importance = await self._score_observation_importance(agent, observation_text, location)
    
    return ActionResult(
        success=True,
        description=f"Observed: {observation_text}",
        energy_cost=2,
        observation=True,
        observation_details={
            "location": location.id,
            "agents_present": [a.id for a in nearby_agents],
            "objects_present": [obj.id for obj in location_objects],
            "importance": importance
        }
    )

async def _execute_wait_action(self, agent: Agent, action: Action) -> ActionResult:
    """Execute wait action with passive observation and recovery."""
    
    location = await self.world_manager.get_agent_location(agent.id)
    
    # Generate wait description based on context
    wait_context = action.parameters.get("reason", "")
    
    if agent.energy < 50:
        description = f"Rested at {location.name}, recovering energy"
        energy_cost = -2  # Waiting restores energy
    elif agent.mood < 5:
        description = f"Took a moment to collect thoughts at {location.name}"
        energy_cost = 0
    else:
        description = f"Waited and observed the activity at {location.name}"
        energy_cost = 1
    
    if wait_context:
        description += f" ({wait_context})"
    
    return ActionResult(
        success=True,
        description=description,
        energy_cost=energy_cost,
        passive_observation=True,
        mood_effect=1 if agent.energy < 30 else 0  # Slight mood boost when tired
    )
```

## 🔄 Action Pipeline

### Pipeline Stages

```python
class ActionExecutionPipeline:
    """Manages the multi-stage action execution pipeline."""
    
    def __init__(self, action_executor: ActionExecutor):
        self.executor = action_executor
        self.pipeline_stages = [
            self._stage_validation,
            self._stage_pre_execution,
            self._stage_execution,
            self._stage_post_execution,
            self._stage_effect_propagation
        ]
    
    async def execute_with_pipeline(self, agent: Agent, action: Action) -> ActionResult:
        """Execute action through complete pipeline with rollback capability."""
        
        execution_context = ActionExecutionContext(
            agent=agent,
            action=action,
            start_time=datetime.now(),
            stage_results={}
        )
        
        try:
            for stage in self.pipeline_stages:
                stage_name = stage.__name__
                stage_start = time.time()
                
                stage_result = await stage(execution_context)
                stage_duration = time.time() - stage_start
                
                execution_context.stage_results[stage_name] = {
                    "result": stage_result,
                    "duration": stage_duration,
                    "success": stage_result.success if hasattr(stage_result, 'success') else True
                }
                
                # Stop pipeline if stage failed
                if hasattr(stage_result, 'success') and not stage_result.success:
                    return stage_result
                
                # Update context with stage result
                if hasattr(stage_result, 'context_updates'):
                    execution_context.update(stage_result.context_updates)
            
            # Pipeline completed successfully
            return execution_context.final_result
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            
            # Attempt rollback
            await self._rollback_execution(execution_context)
            
            return ActionResult(
                success=False,
                description=f"Pipeline failure: {str(e)}",
                energy_cost=1
            )
    
    async def _stage_validation(self, context: ActionExecutionContext) -> StageResult:
        """Validation stage with detailed checks."""
        
        validation_checks = [
            self._validate_agent_state,
            self._validate_action_parameters,
            self._validate_world_constraints,
            self._validate_resource_requirements
        ]
        
        validation_results = []
        
        for check in validation_checks:
            check_result = await check(context.agent, context.action)
            validation_results.append(check_result)
            
            if not check_result.valid:
                return StageResult(
                    success=False,
                    message=f"Validation failed: {check_result.reason}",
                    details={"failed_check": check.__name__, "all_results": validation_results}
                )
        
        return StageResult(
            success=True,
            message="All validations passed",
            details={"validation_results": validation_results}
        )
    
    async def _stage_pre_execution(self, context: ActionExecutionContext) -> StageResult:
        """Pre-execution preparation stage."""
        
        # Reserve resources
        await self._reserve_action_resources(context.agent, context.action)
        
        # Create execution snapshot for rollback
        context.pre_execution_snapshot = await self._create_state_snapshot(context.agent)
        
        # Notify other systems of pending action
        await self._notify_action_pending(context.agent, context.action)
        
        return StageResult(
            success=True,
            message="Pre-execution preparation complete"
        )
    
    async def _stage_execution(self, context: ActionExecutionContext) -> StageResult:
        """Core action execution stage."""
        
        try:
            result = await self.executor._execute_action_by_type(context.agent, context.action)
            context.execution_result = result
            
            return StageResult(
                success=result.success,
                message=result.description,
                details={"action_result": result}
            )
            
        except Exception as e:
            return StageResult(
                success=False,
                message=f"Execution failed: {str(e)}",
                details={"error": str(e)}
            )
    
    async def _stage_post_execution(self, context: ActionExecutionContext) -> StageResult:
        """Post-execution processing stage."""
        
        if not context.execution_result.success:
            return StageResult(success=True, message="Skipped due to execution failure")
        
        # Update agent state
        await self._update_agent_state(context.agent, context.action, context.execution_result)
        
        # Create memories
        await self._create_action_memories(context.agent, context.action, context.execution_result)
        
        # Release reserved resources
        await self._release_action_resources(context.agent, context.action)
        
        return StageResult(
            success=True,
            message="Post-execution processing complete"
        )
    
    async def _stage_effect_propagation(self, context: ActionExecutionContext) -> StageResult:
        """Effect propagation stage for cascading consequences."""
        
        if not context.execution_result.success:
            return StageResult(success=True, message="Skipped due to execution failure")
        
        effects_processed = 0
        
        # Propagate effects to other agents
        if context.execution_result.social_interaction:
            await self._propagate_social_effects(context)
            effects_processed += 1
        
        if context.execution_result.location_change:
            await self._propagate_location_effects(context)
            effects_processed += 1
        
        # Update world state based on action
        await self._propagate_world_effects(context)
        
        context.final_result = context.execution_result
        
        return StageResult(
            success=True,
            message=f"Effect propagation complete ({effects_processed} effects)",
            details={"effects_processed": effects_processed}
        )

class ActionExecutionContext:
    def __init__(self, agent: Agent, action: Action, start_time: datetime):
        self.agent = agent
        self.action = action
        self.start_time = start_time
        self.stage_results = {}
        self.pre_execution_snapshot = None
        self.execution_result = None
        self.final_result = None
    
    def update(self, updates: Dict[str, Any]):
        """Update context with new information."""
        for key, value in updates.items():
            setattr(self, key, value)

class StageResult(BaseModel):
    success: bool
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    context_updates: Dict[str, Any] = Field(default_factory=dict)
```

## 📊 Effect Management

### Cascading Effects System

```python
class EffectManager:
    """Manages cascading effects and consequences of actions."""
    
    def __init__(self, world_manager: WorldManager, memory_manager: MemoryManager):
        self.world_manager = world_manager
        self.memory_manager = memory_manager
        self.effect_handlers = {
            "social_interaction": self._handle_social_effects,
            "location_change": self._handle_location_effects,
            "object_interaction": self._handle_object_effects,
            "mood_change": self._handle_mood_effects
        }
    
    async def propagate_effects(self, action_context: ActionExecutionContext) -> List[Effect]:
        """Propagate all effects from an action."""
        
        effects_applied = []
        result = action_context.execution_result
        
        # Determine which effects to apply
        effect_types = []
        if result.social_interaction:
            effect_types.append("social_interaction")
        if result.location_change:
            effect_types.append("location_change")
        if hasattr(result, 'object_interaction') and result.object_interaction:
            effect_types.append("object_interaction")
        if hasattr(result, 'mood_effect') and result.mood_effect:
            effect_types.append("mood_change")
        
        # Apply each effect type
        for effect_type in effect_types:
            handler = self.effect_handlers.get(effect_type)
            if handler:
                try:
                    effects = await handler(action_context)
                    effects_applied.extend(effects)
                except Exception as e:
                    logger.error(f"Failed to apply {effect_type} effects: {e}")
        
        return effects_applied
    
    async def _handle_social_effects(self, context: ActionExecutionContext) -> List[Effect]:
        """Handle effects of social interactions."""
        
        effects = []
        result = context.execution_result
        
        if not result.interaction_target:
            return effects
        
        # Get target agent
        target_agent = await self.storage.get_agent(result.interaction_target)
        if not target_agent:
            return effects
        
        # Create observation memory for target agent
        interaction_memory = f"{context.agent.name} interacted with me: {result.description}"
        await self.memory_manager.add_memory(
            agent_id=target_agent.id,
            content=interaction_memory,
            memory_type=MemoryType.OBSERVATION,
            metadata={"interaction_initiator": context.agent.id}
        )
        
        effects.append(Effect(
            type="memory_creation",
            target_agent=target_agent.id,
            description=f"Created interaction memory for {target_agent.name}"
        ))
        
        # Mood effects based on interaction quality
        if hasattr(result, 'interaction_details'):
            mood_effect = result.interaction_details.get('mood_effect', 'neutral')
            
            if mood_effect == 'positive':
                target_agent.mood = min(10, target_agent.mood + 1)
                context.agent.mood = min(10, context.agent.mood + 1)
                
                effects.extend([
                    Effect(type="mood_boost", target_agent=target_agent.id, magnitude=1),
                    Effect(type="mood_boost", target_agent=context.agent.id, magnitude=1)
                ])
            
            elif mood_effect == 'negative':
                target_agent.mood = max(1, target_agent.mood - 1)
                
                effects.append(
                    Effect(type="mood_decrease", target_agent=target_agent.id, magnitude=1)
                )
        
        # Update agents in storage
        await self.storage.update_agent(target_agent)
        await self.storage.update_agent(context.agent)
        
        return effects
    
    async def _handle_location_effects(self, context: ActionExecutionContext) -> List[Effect]:
        """Handle effects of location changes."""
        
        effects = []
        result = context.execution_result
        
        if not result.new_location:
            return effects
        
        # Notify other agents at the new location
        other_agents = await self.world_manager.get_agents_at_location(result.new_location)
        other_agents = [a for a in other_agents if a.id != context.agent.id]
        
        for other_agent in other_agents:
            # Create observation memory
            arrival_memory = f"{context.agent.name} arrived at {result.new_location}"
            await self.memory_manager.add_memory(
                agent_id=other_agent.id,
                content=arrival_memory,
                memory_type=MemoryType.OBSERVATION,
                metadata={"arrival_event": True, "arriving_agent": context.agent.id}
            )
            
            effects.append(Effect(
                type="arrival_observation",
                target_agent=other_agent.id,
                description=f"Notified {other_agent.name} of arrival"
            ))
        
        # Location-specific effects
        new_location = await self.world_manager.get_location(result.new_location)
        if new_location and new_location.properties:
            
            # Mood effects from location atmosphere
            atmosphere = new_location.properties.get("atmosphere")
            if atmosphere == "peaceful":
                context.agent.mood = min(10, context.agent.mood + 1)
                effects.append(Effect(type="location_mood_boost", magnitude=1))
            elif atmosphere == "stressful":
                context.agent.mood = max(1, context.agent.mood - 1)
                effects.append(Effect(type="location_mood_decrease", magnitude=1))
            
            # Energy effects from location comfort
            comfort = new_location.properties.get("comfort_level")
            if comfort == "high" and context.agent.energy < 80:
                context.agent.energy = min(100, context.agent.energy + 5)
                effects.append(Effect(type="location_energy_boost", magnitude=5))
        
        await self.storage.update_agent(context.agent)
        
        return effects

class Effect(BaseModel):
    type: str
    target_agent: Optional[str] = None
    description: str
    magnitude: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
```

## 🛡️ Concurrency Control

### Action Ordering and Conflict Resolution

```python
class ConcurrencyController:
    """Manages concurrent action execution and conflict resolution."""
    
    def __init__(self):
        self.agent_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        self.location_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        self.resource_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        self.action_queue: Dict[str, List[QueuedAction]] = defaultdict(list)
    
    async def execute_with_concurrency_control(
        self,
        agent: Agent,
        action: Action,
        executor: ActionExecutor
    ) -> ActionResult:
        """Execute action with proper concurrency control."""
        
        # Determine required locks
        required_locks = await self._determine_required_locks(agent, action)
        
        # Acquire locks in consistent order to prevent deadlocks
        sorted_locks = sorted(required_locks.items())
        
        try:
            # Acquire all required locks
            for lock_type, lock_key in sorted_locks:
                lock = self._get_lock(lock_type, lock_key)
                await lock.acquire()
            
            # Execute action
            result = await executor.execute_action(agent, action)
            
            return result
            
        finally:
            # Release locks in reverse order
            for lock_type, lock_key in reversed(sorted_locks):
                lock = self._get_lock(lock_type, lock_key)
                lock.release()
    
    async def _determine_required_locks(self, agent: Agent, action: Action) -> Dict[str, str]:
        """Determine which locks are needed for this action."""
        
        locks = {
            "agent": agent.id  # Always lock the acting agent
        }
        
        if action.action_type == ActionType.MOVE:
            # Lock both current and target locations
            current_location = await self.world_manager.get_agent_location(agent.id)
            if current_location:
                locks["location"] = current_location.id
            
            target_location = action.parameters.get("target_location")
            if target_location:
                locks["target_location"] = target_location
        
        elif action.action_type == ActionType.INTERACT:
            # Lock current location and target agent
            current_location = await self.world_manager.get_agent_location(agent.id)
            if current_location:
                locks["location"] = current_location.id
            
            target_agent_name = action.parameters.get("target_agent")
            if target_agent_name:
                # Find target agent ID
                target_agent = await self._find_agent_by_name(target_agent_name)
                if target_agent:
                    locks["target_agent"] = target_agent.id
        
        return locks
    
    def _get_lock(self, lock_type: str, lock_key: str) -> asyncio.Lock:
        """Get the appropriate lock for the given type and key."""
        
        if lock_type == "agent" or lock_type == "target_agent":
            return self.agent_locks[lock_key]
        elif lock_type == "location" or lock_type == "target_location":
            return self.location_locks[lock_key]
        elif lock_type == "resource":
            return self.resource_locks[lock_key]
        else:
            # Default to agent locks for unknown types
            return self.agent_locks[lock_key]

class QueuedAction(BaseModel):
    agent: Agent
    action: Action
    priority: int = 0
    queued_at: datetime = Field(default_factory=datetime.now)
    
    def __lt__(self, other):
        # Higher priority first, then by queue time
        if self.priority != other.priority:
            return self.priority > other.priority
        return self.queued_at < other.queued_at
```

## 🎯 Future Enhancements

### Planned Features

1. **Complex Actions**: Multi-step action sequences and macro actions
2. **Conditional Actions**: Actions with branching logic based on conditions
3. **Collaborative Actions**: Actions requiring multiple agents working together
4. **Persistent Effects**: Long-term consequences that affect future actions
5. **Action Learning**: Agents learn more effective action strategies over time

### Research Directions

- Optimal concurrency control algorithms for large-scale agent simulations
- Predictive conflict detection and resolution strategies
- Action sequence optimization for goal achievement
- Emergent behavior analysis from action interactions
- Real-time action validation and correction systems

---

The Action System ensures that agent decisions translate into meaningful world changes while maintaining consistency, performance, and realistic consequences in the simulation environment.
