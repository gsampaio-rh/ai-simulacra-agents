-- Initial schema for AI Simulacra Agents
-- Migration 001: Core tables for agents, memories, events, plans, and world state

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Agents table
CREATE TABLE agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    bio TEXT,
    personality TEXT,
    home_location TEXT,
    relationships TEXT, -- JSON
    memories_count INTEGER DEFAULT 0,
    reflections_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent state table (separated for frequent updates)
CREATE TABLE agent_states (
    agent_id TEXT PRIMARY KEY,
    status TEXT DEFAULT 'active',
    current_location TEXT,
    current_task TEXT,
    energy REAL DEFAULT 100.0,
    mood REAL DEFAULT 5.0,
    last_reflection_time TIMESTAMP,
    importance_accumulator REAL DEFAULT 0.0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
);

-- Memories table
CREATE TABLE memories (
    id TEXT PRIMARY KEY, -- UUID
    agent_id TEXT NOT NULL,
    content TEXT NOT NULL,
    memory_type TEXT DEFAULT 'perception',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    importance_score REAL DEFAULT 0.0,
    embedding_id TEXT, -- Reference to Chroma
    location TEXT,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
);

-- Reflections table
CREATE TABLE reflections (
    id TEXT PRIMARY KEY, -- UUID
    agent_id TEXT NOT NULL,
    content TEXT NOT NULL,
    supporting_memories TEXT, -- JSON array of memory UUIDs
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    importance_score REAL DEFAULT 5.0,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
);

-- Plans table
CREATE TABLE plans (
    id TEXT PRIMARY KEY, -- UUID
    agent_id TEXT NOT NULL,
    plan_type TEXT NOT NULL, -- 'daily', 'hourly', 'task'
    content TEXT NOT NULL, -- JSON plan structure
    date_for DATE, -- For daily plans
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
);

-- World state table
CREATE TABLE world_state (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL, -- 'place', 'object', 'agent_location'
    data TEXT NOT NULL, -- JSON data
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Events table
CREATE TABLE events (
    id TEXT PRIMARY KEY, -- UUID
    event_type TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    agent_id TEXT,
    location TEXT,
    content TEXT NOT NULL,
    parameters TEXT, -- JSON
    observers TEXT, -- JSON array of agent IDs
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE SET NULL
);

-- Places table (normalized from world_state for better queries)
CREATE TABLE places (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    capacity INTEGER DEFAULT 10,
    properties TEXT, -- JSON
    connected_places TEXT, -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Objects table (normalized from world_state)
CREATE TABLE objects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    location TEXT,
    properties TEXT, -- JSON
    interactions TEXT, -- JSON array
    is_movable BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location) REFERENCES places(id)
);

-- Agent locations table (normalized for quick lookups)
CREATE TABLE agent_locations (
    agent_id TEXT PRIMARY KEY,
    place_id TEXT NOT NULL,
    previous_place_id TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
    FOREIGN KEY (place_id) REFERENCES places(id),
    FOREIGN KEY (previous_place_id) REFERENCES places(id)
);

-- Indexes for performance
CREATE INDEX idx_memories_agent_timestamp ON memories(agent_id, timestamp DESC);
CREATE INDEX idx_memories_type ON memories(memory_type);
CREATE INDEX idx_memories_importance ON memories(importance_score DESC);
CREATE INDEX idx_memories_location ON memories(location);

CREATE INDEX idx_reflections_agent_timestamp ON reflections(agent_id, timestamp DESC);

CREATE INDEX idx_events_timestamp ON events(timestamp DESC);
CREATE INDEX idx_events_agent ON events(agent_id);
CREATE INDEX idx_events_location ON events(location);
CREATE INDEX idx_events_type ON events(event_type);

CREATE INDEX idx_plans_agent_date ON plans(agent_id, date_for);
CREATE INDEX idx_plans_status ON plans(status);

CREATE INDEX idx_agent_locations_place ON agent_locations(place_id);

-- Triggers to update timestamps
CREATE TRIGGER update_agent_states_timestamp 
    AFTER UPDATE ON agent_states
    BEGIN
        UPDATE agent_states SET last_updated = CURRENT_TIMESTAMP WHERE agent_id = NEW.agent_id;
    END;

CREATE TRIGGER update_plans_timestamp 
    AFTER UPDATE ON plans
    BEGIN
        UPDATE plans SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

-- Views for common queries
CREATE VIEW agent_status_view AS
SELECT 
    a.id,
    a.name,
    s.status,
    s.current_location,
    s.current_task,
    s.energy,
    a.memories_count,
    a.reflections_count,
    s.last_updated
FROM agents a
LEFT JOIN agent_states s ON a.id = s.agent_id;

CREATE VIEW recent_memories_view AS
SELECT 
    m.*,
    a.name as agent_name
FROM memories m
JOIN agents a ON m.agent_id = a.id
ORDER BY m.timestamp DESC;

CREATE VIEW current_world_view AS
SELECT 
    p.id as place_id,
    p.name as place_name,
    COUNT(al.agent_id) as agent_count,
    GROUP_CONCAT(a.name) as agents_present
FROM places p
LEFT JOIN agent_locations al ON p.id = al.place_id
LEFT JOIN agents a ON al.agent_id = a.id
GROUP BY p.id, p.name;
