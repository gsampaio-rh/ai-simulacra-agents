"""World configuration loading and management."""

import json
import logging
from pathlib import Path
from typing import Dict, List

from ..models.world import Place, WorldObject, WorldConfiguration

logger = logging.getLogger(__name__)


class WorldConfigLoader:
    """Loads and manages world configurations from JSON files."""
    
    def __init__(self, config_file: Path):
        """Initialize with configuration file path.
        
        Args:
            config_file: Path to the world configuration JSON file
        """
        self.config_file = Path(config_file)
    
    def load_world_config(self) -> WorldConfiguration:
        """Load world configuration from file.
        
        Returns:
            WorldConfiguration object
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
        """
        if not self.config_file.exists():
            raise FileNotFoundError(f"World config file not found: {self.config_file}")
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            places = []
            objects = []
            
            # Load places
            for place_data in config_data.get('places', []):
                try:
                    place = Place(**place_data)
                    places.append(place)
                    logger.debug(f"Loaded place: {place.name} ({place.id})")
                except Exception as e:
                    logger.error(f"Failed to load place {place_data.get('id', 'unknown')}: {e}")
                    raise ValueError(f"Invalid place configuration: {e}")
            
            # Load objects
            for object_data in config_data.get('objects', []):
                try:
                    obj = WorldObject(**object_data)
                    objects.append(obj)
                    logger.debug(f"Loaded object: {obj.name} ({obj.id})")
                except Exception as e:
                    logger.error(f"Failed to load object {object_data.get('id', 'unknown')}: {e}")
                    raise ValueError(f"Invalid object configuration: {e}")
            
            world_config = WorldConfiguration(places=places, objects=objects)
            logger.info(f"Successfully loaded world config: {len(places)} places, {len(objects)} objects")
            return world_config
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
        except Exception as e:
            logger.error(f"Failed to load world config: {e}")
            raise
    
    def get_place_by_id(self, place_id: str) -> Place:
        """Get a specific place by ID.
        
        Args:
            place_id: The place ID to find
            
        Returns:
            The Place object
            
        Raises:
            ValueError: If place not found
        """
        world_config = self.load_world_config()
        for place in world_config.places:
            if place.id == place_id:
                return place
        
        raise ValueError(f"Place with ID '{place_id}' not found in configuration")
    
    def get_object_by_id(self, object_id: str) -> WorldObject:
        """Get a specific object by ID.
        
        Args:
            object_id: The object ID to find
            
        Returns:
            The WorldObject
            
        Raises:
            ValueError: If object not found
        """
        world_config = self.load_world_config()
        for obj in world_config.objects:
            if obj.id == object_id:
                return obj
        
        raise ValueError(f"Object with ID '{object_id}' not found in configuration")
    
    def get_objects_at_location(self, place_id: str) -> List[WorldObject]:
        """Get all objects at a specific location.
        
        Args:
            place_id: The place ID to search
            
        Returns:
            List of WorldObject instances at the location
        """
        world_config = self.load_world_config()
        return [obj for obj in world_config.objects if obj.location == place_id]
    
    def validate_config(self) -> Dict[str, List[str]]:
        """Validate the world configuration file.
        
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
        
        place_ids = set()
        
        # Validate places
        for i, place_data in enumerate(config_data.get('places', [])):
            prefix = f"Place {i + 1}"
            
            # Check required fields
            required_fields = ['id', 'name', 'description']
            for field in required_fields:
                if field not in place_data:
                    errors.append(f"{prefix}: Missing required field '{field}'")
            
            # Check for duplicate IDs
            place_id = place_data.get('id')
            if place_id:
                if place_id in place_ids:
                    errors.append(f"{prefix}: Duplicate place ID '{place_id}'")
                else:
                    place_ids.add(place_id)
            
            # Validate place configuration
            try:
                Place(**place_data)
            except Exception as e:
                errors.append(f"{prefix}: Configuration error: {e}")
        
        # Validate objects
        object_ids = set()
        for i, object_data in enumerate(config_data.get('objects', [])):
            prefix = f"Object {i + 1}"
            
            # Check required fields
            required_fields = ['id', 'name', 'description', 'location']
            for field in required_fields:
                if field not in object_data:
                    errors.append(f"{prefix}: Missing required field '{field}'")
            
            # Check for duplicate IDs
            object_id = object_data.get('id')
            if object_id:
                if object_id in object_ids:
                    errors.append(f"{prefix}: Duplicate object ID '{object_id}'")
                else:
                    object_ids.add(object_id)
            
            # Check location exists
            location = object_data.get('location')
            if location and location not in place_ids:
                errors.append(f"{prefix}: References unknown location '{location}'")
            
            # Validate object configuration
            try:
                WorldObject(**object_data)
            except Exception as e:
                errors.append(f"{prefix}: Configuration error: {e}")
        
        # Validate place connections
        for place_data in config_data.get('places', []):
            place_id = place_data.get('id')
            connected_places = place_data.get('connected_places', [])
            
            for connected_id in connected_places:
                if connected_id not in place_ids:
                    warnings.append(
                        f"Place '{place_id}' connects to unknown place '{connected_id}'"
                    )
        
        return {"errors": errors, "warnings": warnings}
    
    @classmethod
    def create_example_config(cls, output_file: Path) -> None:
        """Create an example world configuration file.
        
        Args:
            output_file: Path where to save the example config
        """
        example_config = {
            "places": [
                {
                    "id": "town_square",
                    "name": "Town Square",
                    "description": "The central gathering place of the town with a fountain and benches.",
                    "capacity": 50,
                    "properties": {
                        "atmosphere": "bustling",
                        "weather_dependent": True
                    },
                    "connected_places": ["library", "bakery", "main_street"]
                },
                {
                    "id": "library",
                    "name": "Public Library",
                    "description": "A quiet place filled with books and knowledge.",
                    "capacity": 30,
                    "properties": {
                        "atmosphere": "quiet",
                        "noise_level": "low"
                    },
                    "connected_places": ["town_square"]
                },
                {
                    "id": "bakery",
                    "name": "Corner Bakery",
                    "description": "A warm bakery with the smell of fresh bread and pastries.",
                    "capacity": 15,
                    "properties": {
                        "atmosphere": "cozy",
                        "food_available": True
                    },
                    "connected_places": ["town_square"]
                }
            ],
            "objects": [
                {
                    "id": "fountain",
                    "name": "Town Fountain",
                    "description": "A beautiful fountain in the center of the square.",
                    "location": "town_square",
                    "properties": {
                        "water_feature": True
                    },
                    "interactions": ["sit_by", "listen_to_water", "make_wish"],
                    "is_movable": False
                },
                {
                    "id": "book_collection",
                    "name": "Book Collection",
                    "description": "Thousands of books on every topic imaginable.",
                    "location": "library",
                    "properties": {
                        "searchable": True
                    },
                    "interactions": ["read", "search", "borrow"],
                    "is_movable": False
                }
            ]
        }
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(example_config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Created example world config at {output_file}")
