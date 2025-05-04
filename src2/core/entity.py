from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class Position:
    x: int
    y: int

class Entity:
    """Base class for all game entities."""
    
    def __init__(self, x: int, y: int, name: str, display_name: str):
        self.position = Position(x, y)
        self.name = name
        self.display_name = display_name
        self.properties: Dict[str, Any] = {}
        
    @property
    def x(self) -> int:
        return self.position.x
    
    @x.setter
    def x(self, value: int):
        self.position.x = value
        
    @property
    def y(self) -> int:
        return self.position.y
    
    @y.setter
    def y(self, value: int):
        self.position.y = value
        
    def move(self, dx: int, dy: int) -> None:
        """Move the entity by the given delta."""
        self.x += dx
        self.y += dy
        
    def set_property(self, key: str, value: Any) -> None:
        """Set a custom property on the entity."""
        self.properties[key] = value
        
    def get_property(self, key: str, default: Any = None) -> Any:
        """Get a custom property from the entity."""
        return self.properties.get(key, default)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the entity to a dictionary for serialization."""
        return {
            'x': self.x,
            'y': self.y,
            'name': self.name,
            'display_name': self.display_name,
            'properties': self.properties
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """Create an entity from a dictionary."""
        entity = cls(
            x=data['x'],
            y=data['y'],
            name=data['name'],
            display_name=data['display_name']
        )
        entity.properties = data.get('properties', {})
        return entity 