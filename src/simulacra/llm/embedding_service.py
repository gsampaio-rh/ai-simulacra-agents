"""Embedding service for generating and managing embeddings."""

import logging
from typing import List, Optional

from ..config import Settings
from .ollama_client import OllamaClient, OllamaError

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings using Ollama."""
    
    def __init__(self, settings: Optional[Settings] = None):
        """Initialize embedding service.
        
        Args:
            settings: Application settings (will use defaults if None)
        """
        if settings is None:
            from ..config import get_settings
            settings = get_settings()
        
        self.settings = settings
        self.ollama_client = OllamaClient(
            base_url=settings.ollama_base_url,
            timeout=settings.ollama_timeout
        )
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
            
        Raises:
            OllamaError: If embedding generation fails
        """
        try:
            async with self.ollama_client as client:
                response = await client.embeddings(
                    model=self.settings.ollama_embedding_model,
                    prompt=text
                )
                return response.embedding
                
        except Exception as e:
            logger.error(f"Failed to generate embedding for text: {e}")
            raise OllamaError(f"Embedding generation failed: {str(e)}")
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            OllamaError: If any embedding generation fails
        """
        embeddings = []
        
        async with self.ollama_client as client:
            for i, text in enumerate(texts):
                try:
                    response = await client.embeddings(
                        model=self.settings.ollama_embedding_model,
                        prompt=text
                    )
                    embeddings.append(response.embedding)
                    logger.debug(f"Generated embedding {i+1}/{len(texts)}")
                    
                except Exception as e:
                    logger.error(f"Failed to generate embedding for text {i+1}: {e}")
                    raise OllamaError(f"Batch embedding generation failed at index {i}: {str(e)}")
        
        return embeddings
    
    async def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings for the current model.
        
        Returns:
            Embedding dimension
        """
        try:
            # Generate a test embedding to determine dimension
            test_embedding = await self.generate_embedding("test")
            return len(test_embedding)
            
        except Exception as e:
            logger.error(f"Failed to determine embedding dimension: {e}")
            # Fall back to common dimensions
            if "nomic" in self.settings.ollama_embedding_model.lower():
                return 768
            else:
                return 384  # Common dimension for smaller models
    
    async def health_check(self) -> bool:
        """Check if the embedding service is working.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            async with self.ollama_client as client:
                health = await client.health_check()
                if not health:
                    return False
                
                # Test embedding generation
                await self.generate_embedding("health check")
                return True
                
        except Exception as e:
            logger.warning(f"Embedding service health check failed: {e}")
            return False
