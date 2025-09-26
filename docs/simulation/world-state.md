# Simulation World State

Technical documentation for the world state management system that maintains the simulation environment, tracks agent locations, and manages dynamic world properties.

## 🌍 Overview

The World State system maintains a persistent, queryable representation of the simulation environment. It tracks agent positions, location properties, object states, and temporal changes while providing efficient access patterns for agent decision-making and world updates.

### Key Responsibilities

- **Spatial Tracking**: Maintain agent positions and location relationships
- **State Persistence**: Store and retrieve world state across simulation runs
- **Dynamic Properties**: Support time-based and event-driven world changes
- **Efficient Queries**: Fast lookups for agent decision-making contexts
- **Consistency**: Ensure world state remains coherent across concurrent operations

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────┐
│            World State System           │
├─────────────────────────────────────────┤
│  🗺️ World Manager                       │
│     • Agent location tracking           │
│     • Place and object management       │
│     • Connection graph maintenance      │
├─────────────────────────────────────────┤
│  🏠 Location System                     │
│     • Place definitions and properties  │
│     • Capacity management               │
│     • Dynamic state updates             │
├─────────────────────────────────────────┤
│  📦 Object System                       │
│     • Interactive object management     │
│     • State tracking and persistence    │
│     • Interaction validation            │
├─────────────────────────────────────────┤
│  💾 State Persistence                   │
│     • SQLite storage integration        │
│     • Configuration loading             │
│     • State recovery and validation     │
└─────────────────────────────────────────┘
```

### Core Files

- **`src/simulacra/simulation/world_manager.py`** - World state coordination
- **`src/simulacra/models/world.py`** - World entity data models
- **`src/simulacra/storage/sqlite_store.py`** - World state persistence
- **`config/world.json`** - World configuration definitions

## 🗺️ World Manager

The World Manager serves as the central coordinator for all world state operations.

### Core Responsibilities

```python
class WorldManager:
    def __init__(self, storage: SQLiteStore):
        self.storage = storage
        self.locations: Dict[str, Location] = {}
        self.objects: Dict[str, WorldObject] = {}
        self.agent_locations: Dict[str, str] = {}  # agent_id -> location_id
        self.location_agents: Dict[str, Set[str]] = defaultdict(set)  # location_id -> agent_ids
        
    async def initialize(self, world_config_path: str) -> None:
        """Initialize world state from configuration."""
        await self._load_world_configuration(world_config_path)
        await self._restore_persistent_state()
        await self._validate_world_consistency()
```

### Agent Location Management

```python
async def move_agent(self, agent_id: str, target_location_id: str) -> bool:
    """Move agent to target location with validation."""
    
    # Get current location
    current_location_id = self.agent_locations.get(agent_id)
    current_location = self.locations.get(current_location_id) if current_location_id else None
    target_location = self.locations.get(target_location_id)
    
    # Validate target location exists
    if not target_location:
        logger.warning(f"Target location {target_location_id} does not exist")
        return False
    
    # Validate connection if agent has current location
    if current_location and target_location_id not in current_location.connections:
        logger.warning(f"No connection from {current_location.id} to {target_location_id}")
        return False
    
    # Check capacity
    if target_location.capacity is not None:
        current_occupancy = len(self.location_agents[target_location_id])
        if current_occupancy >= target_location.capacity:
            logger.warning(f"Location {target_location_id} at capacity")
            return False
    
    # Execute move
    if current_location_id:
        self.location_agents[current_location_id].discard(agent_id)
    
    self.agent_locations[agent_id] = target_location_id
    self.location_agents[target_location_id].add(agent_id)
    
    # Persist state
    await self.storage.update_agent_location(agent_id, target_location_id)
    
    logger.info(f"Moved agent {agent_id} to {target_location_id}")
    return True

async def get_agent_location(self, agent_id: str) -> Optional[Location]:
    """Get current location of agent."""
    location_id = self.agent_locations.get(agent_id)
    return self.locations.get(location_id) if location_id else None

async def get_agents_at_location(self, location_id: str) -> List[Agent]:
    """Get all agents currently at a location."""
    agent_ids = self.location_agents.get(location_id, set())
    agents = []
    
    for agent_id in agent_ids:
        agent = await self.storage.get_agent(agent_id)
        if agent:
            agents.append(agent)
    
    return agents
```

### Location Queries and Analysis

```python
async def get_nearby_locations(self, location_id: str, max_distance: int = 2) -> List[Location]:
    """Get locations within specified connection distance."""
    
    if location_id not in self.locations:
        return []
    
    visited = set()
    current_level = {location_id}
    distance = 0
    
    while current_level and distance < max_distance:
        next_level = set()
        
        for loc_id in current_level:
            if loc_id in visited:
                continue
                
            visited.add(loc_id)
            location = self.locations[loc_id]
            
            for connected_id in location.connections:
                if connected_id not in visited:
                    next_level.add(connected_id)
        
        current_level = next_level
        distance += 1
    
    return [self.locations[loc_id] for loc_id in visited if loc_id != location_id]

async def find_agents_in_radius(self, center_location_id: str, radius: int = 1) -> Dict[str, List[Agent]]:
    """Find agents within connection radius of a location."""
    
    nearby_locations = await self.get_nearby_locations(center_location_id, radius)
    nearby_locations.append(self.locations[center_location_id])  # Include center
    
    agents_by_location = {}
    for location in nearby_locations:
        agents = await self.get_agents_at_location(location.id)
        if agents:
            agents_by_location[location.id] = agents
    
    return agents_by_location

async def get_world_snapshot(self) -> WorldSnapshot:
    """Get complete current world state."""
    
    location_states = {}
    for location_id, location in self.locations.items():
        agents = await self.get_agents_at_location(location_id)
        objects = [obj for obj in self.objects.values() if obj.location == location_id]
        
        location_states[location_id] = LocationState(
            location=location,
            agents=agents,
            objects=objects,
            occupancy=len(agents),
            capacity_available=location.capacity - len(agents) if location.capacity else None
        )
    
    return WorldSnapshot(
        timestamp=datetime.now(),
        locations=location_states,
        total_agents=len(self.agent_locations),
        total_locations=len(self.locations),
        total_objects=len(self.objects)
    )
```

## 🏠 Location System

### Location Data Model

```python
class Location(BaseModel):
    id: str
    name: str
    description: str
    capacity: Optional[int] = None
    connections: List[str] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    # Dynamic state (not persisted in config)
    current_occupancy: int = 0
    last_updated: datetime = Field(default_factory=datetime.now)

class LocationState(BaseModel):
    """Runtime state of a location."""
    location: Location
    agents: List[Agent]
    objects: List[WorldObject]
    occupancy: int
    capacity_available: Optional[int]
    
    @property
    def is_full(self) -> bool:
        return (self.location.capacity is not None and 
                self.occupancy >= self.location.capacity)
    
    @property
    def occupancy_rate(self) -> float:
        if self.location.capacity is None:
            return 0.0
        return self.occupancy / self.location.capacity if self.location.capacity > 0 else 0.0
```

### Dynamic Location Properties

```python
class DynamicLocation(Location):
    """Location with time-based property changes."""
    
    def __init__(self, **data):
        super().__init__(**data)
        self.property_schedules: Dict[str, PropertySchedule] = {}
    
    def add_property_schedule(self, property_name: str, schedule: PropertySchedule):
        """Add time-based property changes."""
        self.property_schedules[property_name] = schedule
    
    def update_dynamic_properties(self, current_time: datetime):
        """Update properties based on current time."""
        for prop_name, schedule in self.property_schedules.items():
            new_value = schedule.get_value_at_time(current_time)
            if new_value is not None:
                self.properties[prop_name] = new_value

class PropertySchedule:
    """Defines how a property changes over time."""
    
    def __init__(self, schedule_type: str, schedule_data: Dict[str, Any]):
        self.schedule_type = schedule_type
        self.schedule_data = schedule_data
    
    def get_value_at_time(self, current_time: datetime) -> Any:
        """Get property value at specific time."""
        
        if self.schedule_type == "daily_cycle":
            # Value changes based on hour of day
            hour = current_time.hour
            hourly_values = self.schedule_data.get("hourly_values", {})
            return hourly_values.get(str(hour))
        
        elif self.schedule_type == "conditional":
            # Value changes based on conditions
            conditions = self.schedule_data.get("conditions", [])
            for condition in conditions:
                if self._evaluate_condition(condition, current_time):
                    return condition.get("value")
        
        return None
    
    def _evaluate_condition(self, condition: Dict, current_time: datetime) -> bool:
        """Evaluate time-based condition."""
        
        condition_type = condition.get("type")
        
        if condition_type == "time_range":
            start_hour = condition.get("start_hour", 0)
            end_hour = condition.get("end_hour", 23)
            current_hour = current_time.hour
            return start_hour <= current_hour <= end_hour
        
        elif condition_type == "day_of_week":
            target_days = condition.get("days", [])
            current_day = current_time.strftime("%A").lower()
            return current_day in target_days
        
        return False
```

### Location Configuration Loading

```python
async def _load_world_configuration(self, config_path: str) -> None:
    """Load world configuration from JSON file."""
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Load locations
        for location_data in config.get("places", []):
            location = Location(**location_data)
            self.locations[location.id] = location
            self.location_agents[location.id] = set()
        
        # Load objects
        for object_data in config.get("objects", []):
            world_object = WorldObject(**object_data)
            self.objects[world_object.id] = world_object
        
        logger.info(f"Loaded {len(self.locations)} locations and {len(self.objects)} objects")
        
    except Exception as e:
        logger.error(f"Failed to load world configuration: {e}")
        raise

async def _validate_world_consistency(self) -> None:
    """Validate world configuration for consistency."""
    
    errors = []
    
    # Validate location connections
    for location in self.locations.values():
        for connection_id in location.connections:
            if connection_id not in self.locations:
                errors.append(f"Location {location.id} references non-existent connection {connection_id}")
    
    # Validate object locations
    for obj in self.objects.values():
        if obj.location not in self.locations:
            errors.append(f"Object {obj.id} references non-existent location {obj.location}")
    
    # Validate bi-directional connections (optional but recommended)
    for location in self.locations.values():
        for connection_id in location.connections:
            connected_location = self.locations.get(connection_id)
            if connected_location and location.id not in connected_location.connections:
                logger.warning(f"Unidirectional connection: {location.id} -> {connection_id}")
    
    if errors:
        error_msg = "World configuration errors:\n" + "\n".join(errors)
        logger.error(error_msg)
        raise ValueError(error_msg)
```

## 📦 Object System

### Object Data Model

```python
class WorldObject(BaseModel):
    id: str
    name: str
    description: str
    location: str
    interactions: List[str] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)
    state: Dict[str, Any] = Field(default_factory=dict)
    
    # Interaction history
    last_interaction: Optional[datetime] = None
    interaction_count: int = 0

class ObjectInteraction(BaseModel):
    """Record of agent-object interaction."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    object_id: str
    interaction_type: str
    timestamp: datetime = Field(default_factory=datetime.now)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[str] = None
    success: bool = True
```

### Object Interaction System

```python
async def interact_with_object(
    self,
    agent_id: str,
    object_id: str,
    interaction_type: str,
    parameters: Optional[Dict[str, Any]] = None
) -> ObjectInteractionResult:
    """Execute agent interaction with world object."""
    
    # Validate object exists
    obj = self.objects.get(object_id)
    if not obj:
        return ObjectInteractionResult(
            success=False,
            message=f"Object {object_id} not found"
        )
    
    # Validate agent is at object location
    agent_location = await self.get_agent_location(agent_id)
    if not agent_location or agent_location.id != obj.location:
        return ObjectInteractionResult(
            success=False,
            message=f"Agent not at object location {obj.location}"
        )
    
    # Validate interaction type
    if interaction_type not in obj.interactions:
        return ObjectInteractionResult(
            success=False,
            message=f"Interaction '{interaction_type}' not available for {obj.name}"
        )
    
    # Execute interaction based on type
    result = await self._execute_object_interaction(obj, interaction_type, parameters or {})
    
    # Update object state
    obj.last_interaction = datetime.now()
    obj.interaction_count += 1
    
    # Record interaction
    interaction = ObjectInteraction(
        agent_id=agent_id,
        object_id=object_id,
        interaction_type=interaction_type,
        parameters=parameters or {},
        result=result.message,
        success=result.success
    )
    
    await self.storage.record_object_interaction(interaction)
    
    return result

async def _execute_object_interaction(
    self,
    obj: WorldObject,
    interaction_type: str,
    parameters: Dict[str, Any]
) -> ObjectInteractionResult:
    """Execute specific object interaction logic."""
    
    # Coffee machine example
    if obj.id == "espresso_machine" and interaction_type == "make_coffee":
        beans_available = obj.state.get("coffee_beans", 0)
        water_available = obj.state.get("water_level", 0)
        
        if beans_available < 10:
            return ObjectInteractionResult(
                success=False,
                message="Not enough coffee beans"
            )
        
        if water_available < 20:
            return ObjectInteractionResult(
                success=False,
                message="Water level too low"
            )
        
        # Consume resources
        obj.state["coffee_beans"] = beans_available - 10
        obj.state["water_level"] = water_available - 20
        obj.state["last_maintenance"] = datetime.now().isoformat()
        
        return ObjectInteractionResult(
            success=True,
            message="Made delicious espresso",
            state_changes={
                "coffee_beans": obj.state["coffee_beans"],
                "water_level": obj.state["water_level"]
            }
        )
    
    # Garden bed example
    elif obj.id.startswith("garden_bed") and interaction_type == "water":
        current_water = obj.state.get("water_level", "dry")
        growth_stage = obj.state.get("growth_stage", "seedling")
        
        obj.state["water_level"] = "adequate"
        obj.state["last_watered"] = datetime.now().isoformat()
        
        # Advance growth if conditions are right
        if current_water == "dry" and growth_stage == "seedling":
            obj.state["growth_stage"] = "growing"
        
        return ObjectInteractionResult(
            success=True,
            message=f"Watered the {obj.name}",
            state_changes={"water_level": "adequate"}
        )
    
    # Default interaction
    return ObjectInteractionResult(
        success=True,
        message=f"Interacted with {obj.name} using {interaction_type}"
    )

class ObjectInteractionResult(BaseModel):
    success: bool
    message: str
    state_changes: Dict[str, Any] = Field(default_factory=dict)
    effects: List[str] = Field(default_factory=list)
```

## 💾 State Persistence

### World State Storage

```python
async def save_world_state(self) -> None:
    """Persist current world state to database."""
    
    # Save agent locations
    for agent_id, location_id in self.agent_locations.items():
        await self.storage.update_agent_location(agent_id, location_id)
    
    # Save object states
    for obj in self.objects.values():
        await self.storage.update_object_state(obj.id, obj.state, obj.properties)
    
    # Save location dynamic properties
    for location in self.locations.values():
        if hasattr(location, 'properties') and location.properties:
            await self.storage.update_location_properties(location.id, location.properties)

async def restore_world_state(self) -> None:
    """Restore world state from database."""
    
    # Restore agent locations
    agent_locations = await self.storage.get_all_agent_locations()
    for agent_id, location_id in agent_locations.items():
        if location_id in self.locations:
            self.agent_locations[agent_id] = location_id
            self.location_agents[location_id].add(agent_id)
    
    # Restore object states
    object_states = await self.storage.get_all_object_states()
    for object_id, state_data in object_states.items():
        if object_id in self.objects:
            self.objects[object_id].state.update(state_data.get("state", {}))
            self.objects[object_id].properties.update(state_data.get("properties", {}))
    
    logger.info(f"Restored world state: {len(self.agent_locations)} agent locations, {len(object_states)} object states")
```

### Database Schema

```sql
-- Agent location tracking
CREATE TABLE agent_locations (
    agent_id TEXT PRIMARY KEY,
    location_id TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (agent_id) REFERENCES agents (id),
    INDEX idx_location_agents (location_id, updated_at)
);

-- Object state persistence
CREATE TABLE object_states (
    object_id TEXT PRIMARY KEY,
    state TEXT NOT NULL,  -- JSON blob
    properties TEXT,      -- JSON blob  
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Object interaction history
CREATE TABLE object_interactions (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    object_id TEXT NOT NULL,
    interaction_type TEXT NOT NULL,
    parameters TEXT,      -- JSON blob
    result TEXT,
    success BOOLEAN DEFAULT true,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (agent_id) REFERENCES agents (id),
    INDEX idx_object_interactions (object_id, timestamp),
    INDEX idx_agent_interactions (agent_id, timestamp)
);

-- Location property changes (for dynamic locations)
CREATE TABLE location_properties (
    location_id TEXT NOT NULL,
    properties TEXT NOT NULL,  -- JSON blob
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (location_id),
    INDEX idx_location_updates (updated_at)
);
```

## 📊 World Analytics

### World State Monitoring

```python
async def get_world_statistics(self) -> WorldStatistics:
    """Generate comprehensive world statistics."""
    
    # Location statistics
    location_stats = {}
    total_capacity = 0
    total_occupancy = 0
    
    for location in self.locations.values():
        agents = await self.get_agents_at_location(location.id)
        occupancy = len(agents)
        
        location_stats[location.id] = {
            "name": location.name,
            "occupancy": occupancy,
            "capacity": location.capacity,
            "occupancy_rate": occupancy / location.capacity if location.capacity else 0.0,
            "agents": [agent.name for agent in agents]
        }
        
        if location.capacity:
            total_capacity += location.capacity
            total_occupancy += occupancy
    
    # Object interaction statistics
    object_stats = {}
    for obj in self.objects.values():
        recent_interactions = await self.storage.get_object_interactions(
            obj.id, 
            since=datetime.now() - timedelta(hours=24)
        )
        
        object_stats[obj.id] = {
            "name": obj.name,
            "location": obj.location,
            "total_interactions": obj.interaction_count,
            "recent_interactions": len(recent_interactions),
            "last_interaction": obj.last_interaction,
            "current_state": dict(obj.state)
        }
    
    # Connection analysis
    connection_graph = self._analyze_connection_graph()
    
    return WorldStatistics(
        total_locations=len(self.locations),
        total_objects=len(self.objects),
        total_agents=len(self.agent_locations),
        total_capacity=total_capacity,
        total_occupancy=total_occupancy,
        overall_occupancy_rate=total_occupancy / total_capacity if total_capacity > 0 else 0.0,
        location_statistics=location_stats,
        object_statistics=object_stats,
        connection_analysis=connection_graph,
        snapshot_time=datetime.now()
    )

def _analyze_connection_graph(self) -> Dict[str, Any]:
    """Analyze world topology and connectivity."""
    
    # Build adjacency graph
    graph = {loc_id: location.connections for loc_id, location in self.locations.items()}
    
    # Calculate connectivity metrics
    total_connections = sum(len(connections) for connections in graph.values())
    avg_connections = total_connections / len(graph) if graph else 0
    
    # Find most connected locations
    connection_counts = [(loc_id, len(connections)) for loc_id, connections in graph.items()]
    connection_counts.sort(key=lambda x: x[1], reverse=True)
    
    # Check for isolated locations
    isolated_locations = [loc_id for loc_id, connections in graph.items() if not connections]
    
    # Calculate shortest paths (basic implementation)
    path_lengths = self._calculate_shortest_paths(graph)
    avg_path_length = sum(path_lengths.values()) / len(path_lengths) if path_lengths else 0
    
    return {
        "total_connections": total_connections,
        "average_connections_per_location": avg_connections,
        "most_connected_locations": connection_counts[:5],
        "isolated_locations": isolated_locations,
        "average_path_length": avg_path_length,
        "graph_diameter": max(path_lengths.values()) if path_lengths else 0
    }
```

## 🚀 Performance Optimization

### Efficient Location Queries

```python
# Cache frequently accessed data
@lru_cache(maxsize=100)
def get_location_connections(self, location_id: str) -> List[str]:
    """Get cached location connections."""
    location = self.locations.get(location_id)
    return location.connections if location else []

# Batch agent location updates
async def batch_move_agents(self, moves: List[Tuple[str, str]]) -> List[bool]:
    """Execute multiple agent moves efficiently."""
    
    results = []
    updates = []
    
    for agent_id, target_location_id in moves:
        # Validate move
        if await self._validate_move(agent_id, target_location_id):
            # Update in-memory state
            current_location_id = self.agent_locations.get(agent_id)
            if current_location_id:
                self.location_agents[current_location_id].discard(agent_id)
            
            self.agent_locations[agent_id] = target_location_id
            self.location_agents[target_location_id].add(agent_id)
            
            updates.append((agent_id, target_location_id))
            results.append(True)
        else:
            results.append(False)
    
    # Batch database updates
    if updates:
        await self.storage.batch_update_agent_locations(updates)
    
    return results

# Spatial indexing for large worlds
class SpatialIndex:
    def __init__(self, locations: Dict[str, Location]):
        self.locations = locations
        self.distance_cache = {}
        self._build_distance_matrix()
    
    def _build_distance_matrix(self):
        """Pre-compute distances between all location pairs."""
        for loc1_id in self.locations:
            for loc2_id in self.locations:
                if loc1_id != loc2_id:
                    distance = self._calculate_shortest_path(loc1_id, loc2_id)
                    self.distance_cache[(loc1_id, loc2_id)] = distance
    
    def get_distance(self, loc1_id: str, loc2_id: str) -> Optional[int]:
        """Get cached distance between locations."""
        return self.distance_cache.get((loc1_id, loc2_id))
    
    def find_locations_within_distance(self, center_id: str, max_distance: int) -> List[str]:
        """Find all locations within specified distance."""
        nearby = []
        for loc_id in self.locations:
            if loc_id != center_id:
                distance = self.get_distance(center_id, loc_id)
                if distance is not None and distance <= max_distance:
                    nearby.append(loc_id)
        return nearby
```

## 🎯 Future Enhancements

### Planned Features

1. **Dynamic World Events**: Weather, time-of-day effects, and environmental changes
2. **Resource Systems**: Consumable resources and economic modeling
3. **Physics Simulation**: Basic physics for object interactions and environmental effects
4. **Procedural Content**: Algorithmic generation of locations and objects
5. **Multi-layered Worlds**: Indoor/outdoor spaces and hierarchical location systems

### Research Directions

- Optimal world topology for agent social behavior emergence
- Dynamic property systems for realistic environmental simulation
- Efficient spatial data structures for large-scale world simulation
- Agent movement pattern analysis and prediction
- Environmental influence on agent mood and decision-making

---

The World State system provides the foundational environment where agent cognition meets physical reality, enabling rich, persistent, and scalable simulation experiences.
