#!/usr/bin/env python3
"""Environment setup script for AI Simulacra Agents."""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from simulacra.config import get_settings
from simulacra.llm import OllamaClient, EmbeddingService, ImportanceScorer, LLMService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def check_ollama_connection():
    """Check if Ollama is running and accessible."""
    settings = get_settings()
    
    logger.info(f"Checking Ollama connection at {settings.ollama_base_url}...")
    
    try:
        async with OllamaClient(settings.ollama_base_url, timeout=10.0) as client:
            # Test basic connectivity
            health = await client.health_check()
            if not health:
                logger.error("❌ Ollama is not responding")
                return False
            
            logger.info("✅ Ollama is responding")
            
            # List available models
            models = await client.list_models()
            logger.info(f"📋 Available models: {len(models)}")
            
            model_names = [model.get("name", "unknown") for model in models]
            for model_name in model_names:
                logger.info(f"  - {model_name}")
            
            # Check required models
            required_models = [settings.ollama_model, settings.ollama_embedding_model]
            missing_models = []
            
            for required_model in required_models:
                if not any(required_model in model_name for model_name in model_names):
                    missing_models.append(required_model)
            
            if missing_models:
                logger.warning("⚠️ Missing required models:")
                for model in missing_models:
                    logger.warning(f"  - {model}")
                logger.info("Please install missing models with: ollama pull <model_name>")
            else:
                logger.info("✅ All required models are available")
            
            return len(missing_models) == 0
            
    except Exception as e:
        logger.error(f"❌ Failed to connect to Ollama: {e}")
        logger.info("Make sure Ollama is installed and running:")
        logger.info("  1. Install: https://ollama.ai/")
        logger.info("  2. Start: ollama serve")
        logger.info(f"  3. Install models: ollama pull {settings.ollama_model}")
        return False


async def test_services():
    """Test all LLM services."""
    settings = get_settings()
    
    logger.info("Testing LLM services...")
    
    # Test embedding service
    try:
        embedding_service = EmbeddingService(settings)
        health = await embedding_service.health_check()
        if health:
            logger.info("✅ Embedding service is working")
            
            # Test embedding generation
            embedding = await embedding_service.generate_embedding("test")
            logger.info(f"📏 Embedding dimension: {len(embedding)}")
        else:
            logger.error("❌ Embedding service failed health check")
            return False
    except Exception as e:
        logger.error(f"❌ Embedding service error: {e}")
        return False
    
    # Test importance scorer
    try:
        scorer = ImportanceScorer(settings)
        health = await scorer.health_check()
        if health:
            logger.info("✅ Importance scorer is working")
        else:
            logger.error("❌ Importance scorer failed health check")
            return False
    except Exception as e:
        logger.error(f"❌ Importance scorer error: {e}")
        return False
    
    # Test LLM service
    try:
        llm_service = LLMService(settings)
        health = await llm_service.health_check()
        if health:
            logger.info("✅ LLM service is working")
        else:
            logger.error("❌ LLM service failed health check")
            return False
    except Exception as e:
        logger.error(f"❌ LLM service error: {e}")
        return False
    
    return True


def check_configuration():
    """Check configuration files and settings."""
    logger.info("Checking configuration...")
    
    try:
        settings = get_settings()
        
        # Check config files exist
        if not settings.agents_config_path.exists():
            logger.error(f"❌ Agents config file not found: {settings.agents_config_path}")
            return False
        
        if not settings.world_config_path.exists():
            logger.error(f"❌ World config file not found: {settings.world_config_path}")
            return False
        
        logger.info("✅ Configuration files found")
        
        # Check data directories
        settings.sqlite_db_full_path.parent.mkdir(parents=True, exist_ok=True)
        settings.chroma_persist_full_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ Data directories ready")
        
        # Validate settings
        try:
            settings.validate_retrieval_weights()
            logger.info("✅ Settings validation passed")
        except ValueError as e:
            logger.error(f"❌ Settings validation failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration check failed: {e}")
        return False


async def main():
    """Main setup function."""
    logger.info("🚀 Setting up AI Simulacra Agents environment")
    
    # Check configuration
    if not check_configuration():
        logger.error("❌ Configuration check failed")
        sys.exit(1)
    
    # Check Ollama
    if not await check_ollama_connection():
        logger.error("❌ Ollama setup incomplete")
        sys.exit(1)
    
    # Test services
    if not await test_services():
        logger.error("❌ Service tests failed")
        sys.exit(1)
    
    logger.info("🎉 Environment setup complete!")
    logger.info("You can now run: python scripts/init_db.py")


if __name__ == "__main__":
    asyncio.run(main())
