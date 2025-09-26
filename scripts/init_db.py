#!/usr/bin/env python3
"""Database initialization script for AI Simulacra Agents."""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from simulacra.config import get_settings, AgentConfigLoader, WorldConfigLoader
from simulacra.storage import SQLiteStore, VectorStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def initialize_database():
    """Initialize the SQLite database with schema and sample data."""
    settings = get_settings()
    
    logger.info("Initializing SQLite database...")
    
    # Initialize SQLite store
    sqlite_store = SQLiteStore(settings.sqlite_db_path)
    
    try:
        # Create schema
        await sqlite_store.initialize_schema()
        logger.info("✅ SQLite schema initialized")
        
        # Load and create world configuration
        world_loader = WorldConfigLoader(settings.world_config_path)
        world_config = world_loader.load_world_config()
        
        # Create places
        for place in world_config.places:
            await sqlite_store.create_place(place)
        logger.info(f"✅ Created {len(world_config.places)} places")
        
        # Create objects
        for obj in world_config.objects:
            await sqlite_store.create_object(obj)
        logger.info(f"✅ Created {len(world_config.objects)} objects")
        
        # Load and create agents
        agent_loader = AgentConfigLoader(settings.agents_config_path)
        agents = agent_loader.load_agents()
        
        for agent in agents:
            await sqlite_store.create_agent(agent)
            # Set initial location to home
            from simulacra.models.world import AgentLocation
            location = AgentLocation(
                agent_id=agent.id,
                place_id=agent.home_location
            )
            await sqlite_store.update_agent_location(location)
        
        logger.info(f"✅ Created {len(agents)} agents")
        
        # Get database stats
        stats = await sqlite_store.get_database_stats()
        logger.info("📊 Database statistics:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise
    finally:
        await sqlite_store.disconnect()


def initialize_vector_store():
    """Initialize the Chroma vector store."""
    settings = get_settings()
    
    logger.info("Initializing Chroma vector store...")
    
    try:
        # Initialize vector store
        vector_store = VectorStore(settings.chroma_persist_dir)
        vector_store.initialize_collections()
        
        # Get collection stats
        stats = vector_store.get_collection_stats()
        logger.info("✅ Chroma collections initialized")
        logger.info("📊 Vector store statistics:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize vector store: {e}")
        raise


def validate_configurations():
    """Validate configuration files."""
    settings = get_settings()
    
    logger.info("Validating configuration files...")
    
    # Validate agent config
    agent_loader = AgentConfigLoader(settings.agents_config_path)
    agent_validation = agent_loader.validate_config()
    
    if agent_validation["errors"]:
        logger.error("❌ Agent configuration errors:")
        for error in agent_validation["errors"]:
            logger.error(f"  {error}")
        return False
    
    if agent_validation["warnings"]:
        logger.warning("⚠️ Agent configuration warnings:")
        for warning in agent_validation["warnings"]:
            logger.warning(f"  {warning}")
    
    logger.info("✅ Agent configuration is valid")
    
    # Validate world config
    world_loader = WorldConfigLoader(settings.world_config_path)
    world_validation = world_loader.validate_config()
    
    if world_validation["errors"]:
        logger.error("❌ World configuration errors:")
        for error in world_validation["errors"]:
            logger.error(f"  {error}")
        return False
    
    if world_validation["warnings"]:
        logger.warning("⚠️ World configuration warnings:")
        for warning in world_validation["warnings"]:
            logger.warning(f"  {warning}")
    
    logger.info("✅ World configuration is valid")
    return True


async def main():
    """Main initialization function."""
    logger.info("🚀 Starting AI Simulacra Agents database initialization")
    
    try:
        # Validate configurations first
        if not validate_configurations():
            logger.error("❌ Configuration validation failed. Please fix errors before proceeding.")
            sys.exit(1)
        
        # Initialize databases
        await initialize_database()
        initialize_vector_store()
        
        logger.info("🎉 Database initialization completed successfully!")
        logger.info("You can now start the simulation service.")
        
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
