"""Unit tests for LLM services."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from simulacra.llm import OllamaClient, EmbeddingService, ImportanceScorer
from simulacra.llm.ollama_client import OllamaResponse, OllamaEmbeddingResponse
from simulacra.models.memory import Memory, MemoryType
from simulacra.models.agent import Agent


class TestOllamaClient:
    """Test Ollama client functionality."""
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, test_settings):
        """Test successful health check."""
        client = OllamaClient(test_settings.ollama_base_url)
        
        # Mock the internal request method
        client._make_request = AsyncMock(return_value={"models": []})
        
        health = await client.health_check()
        assert health is True
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, test_settings):
        """Test failed health check."""
        client = OllamaClient(test_settings.ollama_base_url)
        
        # Mock failure
        client._make_request = AsyncMock(side_effect=Exception("Connection failed"))
        
        health = await client.health_check()
        assert health is False
    
    @pytest.mark.asyncio
    async def test_generate_text(self, test_settings):
        """Test text generation."""
        client = OllamaClient(test_settings.ollama_base_url)
        
        # Mock response
        mock_response = {
            "response": "Hello, world!",
            "model": "test-model",
            "done": True
        }
        client._make_request = AsyncMock(return_value=mock_response)
        
        response = await client.generate(
            model="test-model",
            prompt="Say hello"
        )
        
        assert isinstance(response, OllamaResponse)
        assert response.response == "Hello, world!"
        assert response.model == "test-model"
        assert response.done is True
    
    @pytest.mark.asyncio
    async def test_generate_embeddings(self, test_settings):
        """Test embedding generation."""
        client = OllamaClient(test_settings.ollama_base_url)
        
        # Mock embedding response
        mock_response = {
            "embedding": [0.1, 0.2, 0.3],
            "model": "test-embedding-model"
        }
        client._make_request = AsyncMock(return_value=mock_response)
        
        response = await client.embeddings(
            model="test-embedding-model",
            prompt="test text"
        )
        
        assert isinstance(response, OllamaEmbeddingResponse)
        assert response.embedding == [0.1, 0.2, 0.3]
        assert response.model == "test-embedding-model"


class TestEmbeddingService:
    """Test embedding service functionality."""
    
    @pytest.mark.asyncio
    async def test_generate_embedding(self, test_settings, sample_embedding):
        """Test single embedding generation."""
        service = EmbeddingService(test_settings)
        
        # Mock the Ollama client
        mock_response = OllamaEmbeddingResponse(
            embedding=sample_embedding,
            model=test_settings.ollama_embedding_model
        )
        service.ollama_client.embeddings = AsyncMock(return_value=mock_response)
        service.ollama_client.connect = AsyncMock()
        service.ollama_client.disconnect = AsyncMock()
        
        embedding = await service.generate_embedding("test text")
        
        assert embedding == sample_embedding
        assert len(embedding) == 384  # From fixture
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_batch(self, test_settings, sample_embedding):
        """Test batch embedding generation."""
        service = EmbeddingService(test_settings)
        
        # Mock the Ollama client
        mock_response = OllamaEmbeddingResponse(
            embedding=sample_embedding,
            model=test_settings.ollama_embedding_model
        )
        service.ollama_client.embeddings = AsyncMock(return_value=mock_response)
        service.ollama_client.connect = AsyncMock()
        service.ollama_client.disconnect = AsyncMock()
        
        texts = ["text 1", "text 2", "text 3"]
        embeddings = await service.generate_embeddings_batch(texts)
        
        assert len(embeddings) == 3
        assert all(emb == sample_embedding for emb in embeddings)
    
    @pytest.mark.asyncio
    async def test_get_embedding_dimension(self, test_settings, sample_embedding):
        """Test embedding dimension detection."""
        service = EmbeddingService(test_settings)
        
        # Mock the Ollama client
        mock_response = OllamaEmbeddingResponse(
            embedding=sample_embedding,
            model=test_settings.ollama_embedding_model
        )
        service.ollama_client.embeddings = AsyncMock(return_value=mock_response)
        service.ollama_client.connect = AsyncMock()
        service.ollama_client.disconnect = AsyncMock()
        
        dimension = await service.get_embedding_dimension()
        
        assert dimension == len(sample_embedding)


class TestImportanceScorer:
    """Test importance scoring functionality."""
    
    def test_heuristic_scoring(self, test_settings, sample_memory):
        """Test heuristic importance scoring."""
        scorer = ImportanceScorer(test_settings)
        
        # Test basic memory
        basic_score = scorer._get_heuristic_score(sample_memory)
        assert 1.0 <= basic_score <= 10.0
        
        # Test high-importance memory
        important_memory = Memory(
            agent_id="test",
            content="My friend died in an accident today",
            memory_type=MemoryType.PERCEPTION
        )
        important_score = scorer._get_heuristic_score(important_memory)
        assert important_score > basic_score
        
        # Test reflection memory (inherently important)
        reflection_memory = Memory(
            agent_id="test",
            content="I've been thinking about my relationships",
            memory_type=MemoryType.REFLECTION
        )
        reflection_score = scorer._get_heuristic_score(reflection_memory)
        assert reflection_score > basic_score
    
    @pytest.mark.asyncio
    async def test_importance_scoring_fallback(self, test_settings, sample_memory):
        """Test importance scoring with LLM fallback to heuristic."""
        scorer = ImportanceScorer(test_settings)
        
        # Mock LLM failure
        scorer._get_llm_score = AsyncMock(side_effect=Exception("LLM failed"))
        
        score = await scorer.score_importance(sample_memory)
        
        # Should fall back to heuristic score
        assert 1.0 <= score <= 10.0
    
    @pytest.mark.asyncio
    async def test_importance_scoring_with_llm(self, test_settings, sample_memory):
        """Test importance scoring with successful LLM."""
        scorer = ImportanceScorer(test_settings)
        
        # Mock successful LLM scoring
        scorer._get_llm_score = AsyncMock(return_value=7.5)
        
        score = await scorer.score_importance(sample_memory)
        
        # Should be weighted combination of heuristic and LLM
        assert 1.0 <= score <= 10.0


@pytest.fixture
def mock_agent():
    """Create a mock agent for testing."""
    return Agent(
        id="test_agent",
        name="Test Agent",
        bio="A test agent",
        personality="friendly, curious",
        home_location="test_home"
    )
