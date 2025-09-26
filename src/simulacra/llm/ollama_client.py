"""Ollama client wrapper with error handling and async support."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class OllamaResponse(BaseModel):
    """Response from Ollama API."""
    
    response: str
    model: str
    done: bool
    context: Optional[List[int]] = None
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    eval_count: Optional[int] = None


class OllamaEmbeddingResponse(BaseModel):
    """Embedding response from Ollama API."""
    
    embedding: List[float]
    model: str


class OllamaError(Exception):
    """Custom exception for Ollama-related errors."""
    pass


class OllamaClient:
    """Async HTTP client for Ollama API."""
    
    def __init__(
        self, 
        base_url: str = "http://localhost:11434",
        timeout: float = 120.0,
        max_retries: int = 3
    ):
        """Initialize Ollama client.
        
        Args:
            base_url: Base URL for Ollama API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    async def connect(self) -> None:
        """Initialize HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
            )
    
    async def disconnect(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def _make_request(
        self, 
        endpoint: str, 
        payload: Dict[str, Any],
        retries: int = 0
    ) -> Dict[str, Any]:
        """Make HTTP request to Ollama with retries.
        
        Args:
            endpoint: API endpoint (e.g., '/api/generate')
            payload: Request payload
            retries: Current retry count
            
        Returns:
            Response data as dictionary
            
        Raises:
            OllamaError: If request fails after all retries
        """
        if not self._client:
            await self.connect()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = await self._client.post(url, json=payload)
            response.raise_for_status()
            
            # Handle streaming responses (for generate endpoint)
            if endpoint == "/api/generate" and payload.get("stream", True):
                return await self._handle_streaming_response(response)
            
            return response.json()
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error(f"Ollama request failed: {error_msg}")
            
            # Retry on server errors
            if e.response.status_code >= 500 and retries < self.max_retries:
                wait_time = 2 ** retries  # Exponential backoff
                logger.info(f"Retrying in {wait_time} seconds... (attempt {retries + 1}/{self.max_retries})")
                await asyncio.sleep(wait_time)
                return await self._make_request(endpoint, payload, retries + 1)
            
            raise OllamaError(error_msg)
            
        except httpx.RequestError as e:
            error_msg = f"Request error: {str(e)}"
            logger.error(f"Ollama request failed: {error_msg}")
            
            # Retry on connection errors
            if retries < self.max_retries:
                wait_time = 2 ** retries
                logger.info(f"Retrying in {wait_time} seconds... (attempt {retries + 1}/{self.max_retries})")
                await asyncio.sleep(wait_time)
                return await self._make_request(endpoint, payload, retries + 1)
            
            raise OllamaError(error_msg)
        
        except Exception as e:
            logger.error(f"Unexpected error in Ollama request: {e}")
            raise OllamaError(f"Unexpected error: {str(e)}")
    
    async def _handle_streaming_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle streaming response from Ollama.
        
        Args:
            response: HTTP response object
            
        Returns:
            Combined response data
        """
        full_response = ""
        last_data = {}
        
        async for line in response.aiter_lines():
            if line.strip():
                try:
                    data = json.loads(line)
                    if "response" in data:
                        full_response += data["response"]
                    last_data = data
                    
                    if data.get("done", False):
                        break
                        
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse streaming response line: {line}")
        
        # Return combined response
        last_data["response"] = full_response
        return last_data
    
    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        template: Optional[str] = None,
        context: Optional[List[int]] = None,
        stream: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> OllamaResponse:
        """Generate text using Ollama.
        
        Args:
            model: Model name (e.g., 'llama2:7b')
            prompt: Input prompt
            system: Optional system message
            template: Optional prompt template
            context: Optional context from previous generation
            stream: Whether to stream the response
            options: Additional model options
            
        Returns:
            Generated response
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }
        
        if system:
            payload["system"] = system
        if template:
            payload["template"] = template
        if context:
            payload["context"] = context
        if options:
            payload["options"] = options
        
        try:
            response_data = await self._make_request("/api/generate", payload)
            return OllamaResponse(**response_data)
            
        except Exception as e:
            logger.error(f"Failed to generate text: {e}")
            raise
    
    async def embeddings(self, model: str, prompt: str) -> OllamaEmbeddingResponse:
        """Generate embeddings using Ollama.
        
        Args:
            model: Embedding model name (e.g., 'nomic-embed-text')
            prompt: Text to embed
            
        Returns:
            Embedding vector
        """
        payload = {
            "model": model,
            "prompt": prompt
        }
        
        try:
            response_data = await self._make_request("/api/embeddings", payload)
            return OllamaEmbeddingResponse(**response_data)
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models.
        
        Returns:
            List of model information
        """
        try:
            response_data = await self._make_request("/api/tags", {})
            return response_data.get("models", [])
            
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            raise
    
    async def show_model(self, name: str) -> Dict[str, Any]:
        """Show model information.
        
        Args:
            name: Model name
            
        Returns:
            Model information
        """
        payload = {"name": name}
        
        try:
            return await self._make_request("/api/show", payload)
            
        except Exception as e:
            logger.error(f"Failed to show model {name}: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if Ollama is available and responding.
        
        Returns:
            True if Ollama is healthy, False otherwise
        """
        try:
            await self.list_models()
            return True
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False
