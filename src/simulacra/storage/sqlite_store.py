"""SQLite storage implementation for AI Simulacra Agents."""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

import aiosqlite
from pydantic import BaseModel

logger = logging.getLogger(__name__)

from ..models.agent import Agent, AgentState
from ..models.event import Event
from ..models.memory import Memory, Reflection, MemoryType
from ..models.planning import DailyPlan
from ..models.world import Place, WorldObject, AgentLocation


class SQLiteStore:
    """SQLite-based storage for structured data."""
    
    def __init__(self, db_path: Union[str, Path] = "data/simulacra.db"):
        """Initialize SQLite store.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: Optional[aiosqlite.Connection] = None
    
    async def connect(self) -> None:
        """Establish database connection."""
        if self._connection is None:
            self._connection = await aiosqlite.connect(
                str(self.db_path),
                timeout=30.0
            )
            # Enable foreign keys and WAL mode for better performance
            await self._connection.execute("PRAGMA foreign_keys = ON")
            await self._connection.execute("PRAGMA journal_mode = WAL")
            await self._connection.execute("PRAGMA synchronous = NORMAL")
    
    async def disconnect(self) -> None:
        """Close database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None
    
    async def initialize_schema(self) -> None:
        """Initialize database schema from migration files."""
        await self.connect()
        
        # Read and execute the initial schema
        migrations_dir = Path(__file__).parent / "migrations"
        schema_file = migrations_dir / "001_initial_schema.sql"
        
        if schema_file.exists():
            schema_sql = schema_file.read_text()
            
            # Use executescript for handling complex SQL with triggers
            try:
                # First, let's just execute the whole script at once
                await self._connection.executescript(schema_sql)
                await self._connection.commit()
            except Exception as e:
                if "already exists" in str(e):
                    logger.debug("Schema already exists, continuing...")
                else:
                    logger.error(f"Failed to execute schema: {e}")
                    raise
    
    # Agent operations
    async def create_agent(self, agent: Agent) -> None:
        """Create a new agent in the database."""
        await self.connect()
        
        # Insert agent
        await self._connection.execute("""
            INSERT INTO agents (
                id, name, bio, personality, home_location, 
                relationships, memories_count, reflections_count, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            agent.id,
            agent.name,
            agent.bio,
            agent.personality,
            agent.home_location,
            json.dumps(agent.relationships),
            agent.memories_count,
            agent.reflections_count,
            agent.created_at.isoformat()
        ))
        
        # Insert agent state
        await self._connection.execute("""
            INSERT INTO agent_states (
                agent_id, status, current_location, current_task,
                energy, mood, last_reflection_time, 
                importance_accumulator, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            agent.id,
            agent.state.status.value,
            agent.state.current_location,
            agent.state.current_task,
            agent.state.energy,
            agent.state.mood,
            agent.state.last_reflection_time.isoformat() if agent.state.last_reflection_time else None,
            agent.state.importance_accumulator,
            agent.state.last_updated.isoformat()
        ))
        
        await self._connection.commit()
    
    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Retrieve an agent by ID."""
        await self.connect()
        
        cursor = await self._connection.execute("""
            SELECT 
                a.id, a.name, a.bio, a.personality, a.home_location,
                a.relationships, a.memories_count, a.reflections_count, a.created_at,
                s.status, s.current_location, s.current_task, s.energy, s.mood,
                s.last_reflection_time, s.importance_accumulator, s.last_updated
            FROM agents a
            LEFT JOIN agent_states s ON a.id = s.agent_id
            WHERE a.id = ?
        """, (agent_id,))
        
        row = await cursor.fetchone()
        if not row:
            return None
        
        # Parse the row into an Agent object
        agent_data = {
            "id": row[0],
            "name": row[1],
            "bio": row[2],
            "personality": row[3],
            "home_location": row[4],
            "relationships": json.loads(row[5]) if row[5] else {},
            "memories_count": row[6],
            "reflections_count": row[7],
            "created_at": datetime.fromisoformat(row[8]),
            "state": {
                "agent_id": row[0],
                "status": row[9] or "active",
                "current_location": row[10],
                "current_task": row[11],
                "energy": row[12] or 100.0,
                "mood": row[13] or 5.0,
                "last_reflection_time": datetime.fromisoformat(row[14]) if row[14] else None,
                "importance_accumulator": row[15] or 0.0,
                "last_updated": datetime.fromisoformat(row[16]) if row[16] else datetime.utcnow()
            }
        }
        
        return Agent(**agent_data)
    
    async def update_agent_state(self, agent_state: AgentState) -> None:
        """Update agent state."""
        await self.connect()
        
        await self._connection.execute("""
            UPDATE agent_states SET
                status = ?, current_location = ?, current_task = ?,
                energy = ?, mood = ?, last_reflection_time = ?,
                importance_accumulator = ?
            WHERE agent_id = ?
        """, (
            agent_state.status.value if hasattr(agent_state.status, 'value') else agent_state.status,
            agent_state.current_location,
            agent_state.current_task,
            agent_state.energy,
            agent_state.mood,
            agent_state.last_reflection_time.isoformat() if agent_state.last_reflection_time else None,
            agent_state.importance_accumulator,
            agent_state.agent_id
        ))
        
        await self._connection.commit()
    
    # Memory operations
    async def add_memory(self, memory: Memory) -> None:
        """Add a memory to the database."""
        await self.connect()
        
        await self._connection.execute("""
            INSERT INTO memories (
                id, agent_id, content, memory_type, timestamp,
                importance_score, embedding_id, location
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(memory.id),
            memory.agent_id,
            memory.content,
            memory.memory_type.value if hasattr(memory.memory_type, 'value') else memory.memory_type,
            memory.timestamp.isoformat(),
            memory.importance_score,
            memory.embedding_id,
            memory.location
        ))
        
        # Update agent memory count
        await self._connection.execute("""
            UPDATE agents SET memories_count = memories_count + 1
            WHERE id = ?
        """, (memory.agent_id,))
        
        await self._connection.commit()
    
    async def get_recent_memories(
        self, 
        agent_id: str, 
        limit: int = 10,
        memory_types: Optional[List[str]] = None,
        since: Optional[datetime] = None,
        hours: Optional[int] = None
    ) -> List[Memory]:
        """Get recent memories for an agent."""
        await self.connect()
        
        query = """
            SELECT id, agent_id, content, memory_type, timestamp,
                   importance_score, embedding_id, location
            FROM memories
            WHERE agent_id = ?
        """
        params = [agent_id]
        
        # Add time filtering
        if since:
            query += " AND timestamp >= ?"
            params.append(since.isoformat())
        elif hours:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            query += " AND timestamp >= ?"
            params.append(cutoff_time.isoformat())
        
        if memory_types:
            placeholders = ",".join("?" * len(memory_types))
            query += f" AND memory_type IN ({placeholders})"
            params.extend(memory_types)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor = await self._connection.execute(query, params)
        rows = await cursor.fetchall()
        
        memories = []
        for row in rows:
            memory = Memory(
                id=UUID(row[0]),
                agent_id=row[1],
                content=row[2],
                memory_type=row[3],  # Let the Memory model handle string->enum conversion
                timestamp=datetime.fromisoformat(row[4]),
                importance_score=row[5],
                embedding_id=row[6],
                location=row[7]
            )
            memories.append(memory)
        
        return memories
    
    async def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Get a specific memory by ID."""
        await self.connect()
        
        cursor = await self._connection.execute("""
            SELECT id, agent_id, content, memory_type, timestamp,
                   importance_score, embedding_id, location
            FROM memories
            WHERE id = ?
        """, (memory_id,))
        
        row = await cursor.fetchone()
        if not row:
            return None
        
        return Memory(
            id=UUID(row[0]),
            agent_id=row[1],
            content=row[2],
            memory_type=row[3],  # Let the Memory model handle string->enum conversion
            timestamp=datetime.fromisoformat(row[4]),
            importance_score=row[5],
            embedding_id=row[6],
            location=row[7]
        )
    
    # Event operations
    async def add_event(self, event: Event) -> None:
        """Add an event to the database."""
        await self.connect()
        
        await self._connection.execute("""
            INSERT INTO events (
                id, event_type, timestamp, agent_id, location,
                content, parameters, observers
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(event.id),
            event.event_type.value,
            event.timestamp.isoformat(),
            event.agent_id,
            event.location,
            event.content,
            json.dumps(event.parameters),
            json.dumps(event.observers)
        ))
        
        await self._connection.commit()
    
    # World state operations
    async def create_place(self, place: Place) -> None:
        """Create a place in the world."""
        await self.connect()
        
        await self._connection.execute("""
            INSERT INTO places (
                id, name, description, capacity, properties, connected_places
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            place.id,
            place.name,
            place.description,
            place.capacity,
            json.dumps(place.properties),
            json.dumps(place.connected_places)
        ))
        
        await self._connection.commit()
    
    async def create_object(self, obj: WorldObject) -> None:
        """Create an object in the world."""
        await self.connect()
        
        await self._connection.execute("""
            INSERT INTO objects (
                id, name, description, location, properties, 
                interactions, is_movable
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            obj.id,
            obj.name,
            obj.description,
            obj.location,
            json.dumps(obj.properties),
            json.dumps(obj.interactions),
            obj.is_movable
        ))
        
        await self._connection.commit()
    
    async def update_agent_location(self, agent_location: AgentLocation) -> None:
        """Update an agent's location."""
        await self.connect()
        
        await self._connection.execute("""
            INSERT OR REPLACE INTO agent_locations (
                agent_id, place_id, previous_place_id, last_updated
            ) VALUES (?, ?, ?, ?)
        """, (
            agent_location.agent_id,
            agent_location.place_id,
            agent_location.previous_place_id,
            agent_location.last_updated.isoformat()
        ))
        
        # Also update agent state
        await self._connection.execute("""
            UPDATE agent_states SET current_location = ?
            WHERE agent_id = ?
        """, (agent_location.place_id, agent_location.agent_id))
        
        await self._connection.commit()
    
    async def get_agents_at_location(self, place_id: str) -> List[str]:
        """Get all agent IDs at a specific location."""
        await self.connect()
        
        cursor = await self._connection.execute("""
            SELECT agent_id FROM agent_locations WHERE place_id = ?
        """, (place_id,))
        
        rows = await cursor.fetchall()
        return [row[0] for row in rows]
    
    # Reflection operations
    async def add_reflection(self, reflection: Reflection) -> None:
        """Add a reflection to the database."""
        await self.connect()
        
        await self._connection.execute("""
            INSERT INTO reflections (
                id, agent_id, content, supporting_memories, 
                timestamp, importance_score
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(reflection.id),
            reflection.agent_id,
            reflection.content,
            json.dumps([str(uuid) for uuid in reflection.supporting_memories]),
            reflection.timestamp.isoformat(),
            reflection.importance_score
        ))
        
        await self._connection.commit()
    
    async def get_agent_reflections(
        self, 
        agent_id: str, 
        limit: int = 10
    ) -> List[Reflection]:
        """Get recent reflections for an agent."""
        await self.connect()
        
        cursor = await self._connection.execute("""
            SELECT id, agent_id, content, supporting_memories, 
                   timestamp, importance_score
            FROM reflections
            WHERE agent_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (agent_id, limit))
        
        rows = await cursor.fetchall()
        reflections = []
        
        for row in rows:
            supporting_memories_json = row[3]
            supporting_memories = []
            
            if supporting_memories_json:
                try:
                    memory_strings = json.loads(supporting_memories_json)
                    supporting_memories = [UUID(uuid_str) for uuid_str in memory_strings]
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Failed to parse supporting memories: {e}")
            
            reflection = Reflection(
                id=UUID(row[0]),
                agent_id=row[1],
                content=row[2],
                supporting_memories=supporting_memories,
                timestamp=datetime.fromisoformat(row[4]),
                importance_score=row[5]
            )
            reflections.append(reflection)
        
        return reflections
    
    # Plan storage methods
    async def add_plan(
        self,
        plan_id: str,
        agent_id: str,
        plan_type: str,
        content: str,
        date_for: Optional[datetime.date] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        status: str = "pending"
    ) -> None:
        """Add a new plan to storage."""
        await self.connect()
        
        await self._connection.execute("""
            INSERT OR REPLACE INTO plans (
                id, agent_id, plan_type, content, date_for, 
                start_time, end_time, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            plan_id,
            agent_id,
            plan_type,
            content,
            date_for.isoformat() if date_for else None,
            start_time.isoformat() if start_time else None,
            end_time.isoformat() if end_time else None,
            status,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        await self._connection.commit()
    
    async def get_plans(
        self,
        agent_id: Optional[str] = None,
        plan_type: Optional[str] = None,
        date_for: Optional[datetime.date] = None,
        status: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get plans matching the criteria."""
        await self.connect()
        
        conditions = []
        params = []
        
        if agent_id:
            conditions.append("agent_id = ?")
            params.append(agent_id)
        
        if plan_type:
            conditions.append("plan_type = ?")
            params.append(plan_type)
        
        if date_for:
            conditions.append("date_for = ?")
            params.append(date_for.isoformat())
        
        if status:
            conditions.append("status = ?")
            params.append(status)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        params.append(limit)
        
        cursor = await self._connection.execute(f"""
            SELECT id, agent_id, plan_type, content, date_for, 
                   start_time, end_time, status, created_at, updated_at
            FROM plans
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ?
        """, params)
        
        rows = await cursor.fetchall()
        plans = []
        
        for row in rows:
            plan = {
                "id": row[0],
                "agent_id": row[1],
                "plan_type": row[2],
                "content": row[3],
                "date_for": row[4],
                "start_time": row[5],
                "end_time": row[6],
                "status": row[7],
                "created_at": row[8],
                "updated_at": row[9]
            }
            plans.append(plan)
        
        return plans
    
    async def update_plan_status(self, plan_id: str, status: str) -> bool:
        """Update the status of a plan."""
        await self.connect()
        
        cursor = await self._connection.execute("""
            UPDATE plans 
            SET status = ?, updated_at = ?
            WHERE id = ?
        """, (status, datetime.now().isoformat(), plan_id))
        
        await self._connection.commit()
        return cursor.rowcount > 0
    
    async def delete_plan(self, plan_id: str) -> bool:
        """Delete a plan."""
        await self.connect()
        
        cursor = await self._connection.execute("""
            DELETE FROM plans WHERE id = ?
        """, (plan_id,))
        
        await self._connection.commit()
        return cursor.rowcount > 0

    # Utility methods
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        await self.connect()
        
        stats = {}
        
        # Count records in each table
        tables = ["agents", "memories", "reflections", "events", "places", "objects", "plans"]
        for table in tables:
            cursor = await self._connection.execute(f"SELECT COUNT(*) FROM {table}")
            count = await cursor.fetchone()
            stats[f"{table}_count"] = count[0] if count else 0
        
        return stats
