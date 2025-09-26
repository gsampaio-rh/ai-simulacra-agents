# Storage System Documentation

This directory contains comprehensive documentation for the storage layer that manages persistent data for agents, memories, world state, and simulation history.

## 📚 Storage Components

### Core Storage Systems

- **[SQLite Store](sqlite-store.md)** - Primary relational database for structured data
- **[Vector Store](vector-store.md)** - ChromaDB integration for semantic memory search
- **[Data Models](data-models.md)** - Pydantic schemas and database schemas

### Storage Patterns

- **[Persistence Strategies](persistence-strategies.md)** - Data durability and consistency approaches
- **[Performance Optimization](performance-optimization.md)** - Query optimization and caching
- **[Backup and Recovery](backup-recovery.md)** - Data protection and restoration procedures

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────┐
│            Storage Layer                │
├─────────────────────────────────────────┤
│  🗄️ SQLite Store                       │
│     • Agents, memories, plans           │
│     • World state, locations            │
│     • Simulation history                │
├─────────────────────────────────────────┤
│  🔍 Vector Store (ChromaDB)             │
│     • Memory embeddings                 │
│     • Semantic search                   │
│     • Similarity queries                │
├─────────────────────────────────────────┤
│  📊 Data Management                     │
│     • Schema migrations                 │
│     • Data validation                   │
│     • Consistency enforcement           │
└─────────────────────────────────────────┘
```

## 🗃️ Data Organization

### Primary Data Entities

**Agents**:
- Identity, personality, state
- Location tracking
- Energy, mood, relationships

**Memories**:
- Episodic experiences
- Importance scores
- Vector embeddings
- Metadata and timestamps

**Plans**:
- Daily goals and schedules
- Hierarchical task structures
- Planning status and progress

**World State**:
- Location definitions
- Object states and properties
- Agent-location relationships

**Simulation State**:
- Tick history and performance
- Event logs and analytics
- System metrics

### Storage Distribution

| Data Type | SQLite | ChromaDB | Rationale |
|-----------|---------|----------|-----------|
| Agent State | ✅ | ❌ | Structured, relational queries |
| Memory Content | ✅ | ✅ | Metadata in SQL, embeddings in vector DB |
| Memory Embeddings | ❌ | ✅ | Optimized for similarity search |
| World Locations | ✅ | ❌ | Graph relationships, references |
| Object States | ✅ | ❌ | Structured properties, updates |
| Planning Data | ✅ | ❌ | Hierarchical, time-based queries |
| Simulation Logs | ✅ | ❌ | Time series, analytical queries |

## 🚀 Key Features

### Hybrid Storage Approach

**SQLite Advantages**:
- ACID transactions
- Complex relational queries
- Mature ecosystem
- Single-file simplicity
- Strong consistency

**ChromaDB Advantages**:
- Vector similarity search
- Semantic retrieval
- Scalable embeddings
- Optimized for ML workloads
- Built-in embedding functions

### Performance Characteristics

**SQLite Performance**:
- Excellent for reads and structured queries
- Good write performance for moderate loads
- Optimized indexes for common query patterns
- In-memory caching for hot data

**ChromaDB Performance**:
- Sub-second similarity search
- Efficient vector indexing
- Batch operations support
- Automatic embedding generation

## 📖 Documentation Guide

### For Developers

1. **Start with [Data Models](data-models.md)** - Understand the schema and entity relationships
2. **Read [SQLite Store](sqlite-store.md)** - Learn the primary storage interface
3. **Explore [Vector Store](vector-store.md)** - Understand semantic search capabilities
4. **Review [Performance Optimization](performance-optimization.md)** - Optimize queries and operations

### For System Administrators

1. **Review [Persistence Strategies](persistence-strategies.md)** - Understand data durability
2. **Study [Backup and Recovery](backup-recovery.md)** - Implement data protection
3. **Monitor [Performance Optimization](performance-optimization.md)** - Track system health

### For Researchers

1. **Examine [Data Models](data-models.md)** - Understand data structure for analysis
2. **Use [SQLite Store](sqlite-store.md)** - Extract data for research
3. **Leverage [Vector Store](vector-store.md)** - Analyze semantic patterns

## 🛠️ Common Operations

### Basic Data Access

```python
# Initialize storage
storage = SQLiteStore("data/simulacra.db")
await storage.initialize()

# Agent operations
agent = await storage.get_agent("isabella")
await storage.update_agent(agent)

# Memory operations
memories = await storage.get_recent_memories("isabella", limit=10)
await storage.add_memory(memory)

# Planning operations
plan = await storage.get_plans(agent_id="isabella", plan_type="daily")
await storage.add_plan(plan_id, agent_id, "daily", content)
```

### Semantic Search

```python
# Initialize vector store
vector_store = VectorStore()
await vector_store.initialize()

# Search memories
similar_memories = await vector_store.search_memories(
    agent_id="isabella",
    query="social interactions at cafe",
    limit=5
)

# Add memory with embedding
await vector_store.add_memory(memory)
```

## 🔧 Configuration

### SQLite Configuration

```python
# Database settings
DATABASE_CONFIG = {
    "path": "data/simulacra.db",
    "pragmas": {
        "journal_mode": "WAL",
        "synchronous": "NORMAL",
        "cache_size": 1000,
        "foreign_keys": 1
    }
}
```

### ChromaDB Configuration

```python
# Vector store settings
CHROMA_CONFIG = {
    "path": "data/chroma",
    "collection_name": "agent_memories",
    "embedding_function": "nomic-embed-text",
    "distance_metric": "cosine"
}
```

## 📊 Monitoring and Maintenance

### Health Checks

```python
# Check storage health
stats = await storage.get_database_stats()
vector_stats = await vector_store.get_collection_stats()

# Validate data integrity
integrity_report = await storage.validate_data_integrity()
```

### Maintenance Operations

```python
# Optimize database
await storage.optimize_database()

# Clean up old data
await storage.cleanup_old_data(days=30)

# Backup data
await storage.create_backup("backups/sim_backup.db")
```

## 🎯 Best Practices

### Data Design

1. **Normalize appropriately** - Balance query performance with data consistency
2. **Use indexes wisely** - Index frequently queried columns
3. **Handle embeddings separately** - Keep vector data in ChromaDB
4. **Plan for growth** - Design schemas that can evolve

### Performance

1. **Batch operations** - Group related database operations
2. **Use transactions** - Ensure data consistency
3. **Cache frequent queries** - Reduce database load
4. **Monitor query performance** - Identify slow operations

### Reliability

1. **Regular backups** - Protect against data loss
2. **Validate data integrity** - Check for corruption
3. **Test recovery procedures** - Ensure backups work
4. **Monitor disk space** - Prevent storage exhaustion

---

The storage system provides the foundation for persistent, scalable, and performant data management that enables rich agent cognition and comprehensive simulation analysis.
