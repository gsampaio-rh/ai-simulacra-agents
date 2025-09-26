"""Agent configuration loading and management."""

import json
import logging
from pathlib import Path
from typing import Dict, List

from ..models.agent import Agent, AgentConfiguration

logger = logging.getLogger(__name__)


class AgentConfigLoader:
    """Loads and manages agent configurations from JSON files."""
    
    def __init__(self, config_file: Path):
        """Initialize with configuration file path.
        
        Args:
            config_file: Path to the agents configuration JSON file
        """
        self.config_file = Path(config_file)
    
    def load_agents(self) -> List[Agent]:
        """Load all agents from the configuration file.
        
        Returns:
            List of Agent objects
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
        """
        if not self.config_file.exists():
            raise FileNotFoundError(f"Agent config file not found: {self.config_file}")
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            if 'agents' not in config_data:
                raise ValueError("Config file must contain 'agents' key")
            
            agents = []
            for agent_data in config_data['agents']:
                try:
                    # Validate with AgentConfiguration first
                    agent_config = AgentConfiguration(**agent_data)
                    # Convert to Agent
                    agent = agent_config.to_agent()
                    agents.append(agent)
                    logger.debug(f"Loaded agent: {agent.name} ({agent.id})")
                    
                except Exception as e:
                    logger.error(f"Failed to load agent {agent_data.get('id', 'unknown')}: {e}")
                    raise ValueError(f"Invalid agent configuration: {e}")
            
            logger.info(f"Successfully loaded {len(agents)} agents from {self.config_file}")
            return agents
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
        except Exception as e:
            logger.error(f"Failed to load agents: {e}")
            raise
    
    def load_agent_by_id(self, agent_id: str) -> Agent:
        """Load a specific agent by ID.
        
        Args:
            agent_id: The agent ID to load
            
        Returns:
            The Agent object
            
        Raises:
            ValueError: If agent not found
        """
        agents = self.load_agents()
        for agent in agents:
            if agent.id == agent_id:
                return agent
        
        raise ValueError(f"Agent with ID '{agent_id}' not found in configuration")
    
    def get_agent_ids(self) -> List[str]:
        """Get list of all agent IDs in the configuration.
        
        Returns:
            List of agent IDs
        """
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            return [agent['id'] for agent in config_data.get('agents', [])]
            
        except Exception as e:
            logger.error(f"Failed to get agent IDs: {e}")
            return []
    
    def validate_config(self) -> Dict[str, List[str]]:
        """Validate the agent configuration file.
        
        Returns:
            Dictionary with 'errors' and 'warnings' lists
        """
        errors = []
        warnings = []
        
        if not self.config_file.exists():
            errors.append(f"Configuration file not found: {self.config_file}")
            return {"errors": errors, "warnings": warnings}
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {e}")
            return {"errors": errors, "warnings": warnings}
        
        if 'agents' not in config_data:
            errors.append("Missing 'agents' key in configuration")
            return {"errors": errors, "warnings": warnings}
        
        agent_ids = set()
        for i, agent_data in enumerate(config_data['agents']):
            prefix = f"Agent {i + 1}"
            
            # Check required fields
            required_fields = ['id', 'name', 'bio', 'personality', 'home_location']
            for field in required_fields:
                if field not in agent_data:
                    errors.append(f"{prefix}: Missing required field '{field}'")
            
            # Check for duplicate IDs
            agent_id = agent_data.get('id')
            if agent_id:
                if agent_id in agent_ids:
                    errors.append(f"{prefix}: Duplicate agent ID '{agent_id}'")
                else:
                    agent_ids.add(agent_id)
            
            # Validate agent configuration
            try:
                AgentConfiguration(**agent_data)
            except Exception as e:
                errors.append(f"{prefix}: Configuration error: {e}")
            
            # Check relationships
            relationships = agent_data.get('relationships', {})
            for related_agent_id in relationships.keys():
                if related_agent_id not in [a.get('id') for a in config_data['agents']]:
                    warnings.append(
                        f"{prefix}: Relationship with unknown agent '{related_agent_id}'"
                    )
        
        return {"errors": errors, "warnings": warnings}
    
    @classmethod
    def create_example_config(cls, output_file: Path) -> None:
        """Create an example agent configuration file.
        
        Args:
            output_file: Path where to save the example config
        """
        example_config = {
            "agents": [
                {
                    "id": "alice",
                    "name": "Alice Johnson",
                    "bio": "A friendly neighborhood librarian who loves books and helping people find information.",
                    "personality": "helpful, curious, organized, patient",
                    "home_location": "library",
                    "relationships": {
                        "bob": "friend",
                        "charlie": "colleague"
                    }
                },
                {
                    "id": "bob", 
                    "name": "Bob Smith",
                    "bio": "A local baker who gets up early every morning to make fresh bread for the community.",
                    "personality": "hardworking, cheerful, traditional, community-minded",
                    "home_location": "bakery",
                    "relationships": {
                        "alice": "friend"
                    }
                }
            ]
        }
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(example_config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Created example agent config at {output_file}")
