"""Application settings and configuration."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables and config files."""
    
    # Application settings
    app_name: str = Field(default="AI Simulacra Agents", env="APP_NAME")
    version: str = Field(default="0.1.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Database settings
    sqlite_db_path: str = Field(default="data/simulacra.db", env="SQLITE_DB_PATH")
    chroma_persist_dir: str = Field(default="data/chroma", env="CHROMA_PERSIST_DIR")
    
    # Ollama settings
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3.2:3b", env="OLLAMA_MODEL")
    ollama_embedding_model: str = Field(default="nomic-embed-text", env="OLLAMA_EMBEDDING_MODEL")
    ollama_timeout: int = Field(default=120, env="OLLAMA_TIMEOUT")
    
    # Simulation settings
    tick_duration_minutes: int = Field(default=5, env="TICK_DURATION_MINUTES")
    reflection_threshold: float = Field(default=30.0, env="REFLECTION_THRESHOLD")
    max_agents: int = Field(default=50, env="MAX_AGENTS")
    
    # Retrieval settings
    default_memory_limit: int = Field(default=10, env="DEFAULT_MEMORY_LIMIT")
    semantic_weight: float = Field(default=0.6, env="SEMANTIC_WEIGHT")
    recency_weight: float = Field(default=0.2, env="RECENCY_WEIGHT")
    importance_weight: float = Field(default=0.2, env="IMPORTANCE_WEIGHT")
    recency_decay_hours: float = Field(default=24.0, env="RECENCY_DECAY_HOURS")
    
    # API settings
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_workers: int = Field(default=1, env="API_WORKERS")
    
    # Configuration file paths
    config_dir: str = Field(default="config", env="CONFIG_DIR")
    agents_config_file: str = Field(default="agents.json", env="AGENTS_CONFIG_FILE")
    world_config_file: str = Field(default="world.json", env="WORLD_CONFIG_FILE")
    
    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    @property
    def agents_config_path(self) -> Path:
        """Get full path to agents configuration file."""
        return Path(self.config_dir) / self.agents_config_file
    
    @property
    def world_config_path(self) -> Path:
        """Get full path to world configuration file."""
        return Path(self.config_dir) / self.world_config_file
    
    @property
    def sqlite_db_full_path(self) -> Path:
        """Get full path to SQLite database file."""
        return Path(self.sqlite_db_path)
    
    @property
    def chroma_persist_full_path(self) -> Path:
        """Get full path to Chroma persistence directory."""
        return Path(self.chroma_persist_dir)
    
    def validate_retrieval_weights(self) -> None:
        """Validate that retrieval weights sum to 1.0."""
        total_weight = self.semantic_weight + self.recency_weight + self.importance_weight
        if abs(total_weight - 1.0) > 1e-6:
            raise ValueError(f"Retrieval weights must sum to 1.0, got {total_weight}")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    settings = Settings()
    settings.validate_retrieval_weights()
    return settings
