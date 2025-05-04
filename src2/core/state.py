from enum import Enum, auto
from typing import Dict, Set, Optional
from core.entity import Entity
from core.map import GameMap

class GameStateType(Enum):
    NORMAL = auto()
    INVENTORY = auto()
    ITEM_SELECTION = auto()
    CONSOLE = auto()

class GameState:
    """Manages the game state and entity positions."""
    
    def __init__(self, game_map: GameMap):
        self.game_map = game_map
        self.state_type = GameStateType.NORMAL
        self.entities: Dict[tuple, Set[Entity]] = {}  # (x, y) -> {entities}
        self.explored_rooms: Set[int] = set()
        self.turn = 0
        
    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the game state."""
        pos = (entity.x, entity.y)
        if pos not in self.entities:
            self.entities[pos] = set()
        self.entities[pos].add(entity)
        
    def remove_entity(self, entity: Entity) -> None:
        """Remove an entity from the game state."""
        pos = (entity.x, entity.y)
        if pos in self.entities:
            self.entities[pos].discard(entity)
            if not self.entities[pos]:
                del self.entities[pos]
                
    def get_entities_at(self, x: int, y: int) -> Set[Entity]:
        """Get all entities at a position."""
        return self.entities.get((x, y), set())
        
    def move_entity(self, entity: Entity, new_x: int, new_y: int) -> bool:
        """Move an entity to a new position."""
        if not self.game_map.is_walkable(new_x, new_y):
            return False
            
        # Check if the new position is occupied by another character
        entities_at_new_pos = self.get_entities_at(new_x, new_y)
        if any(isinstance(e, Entity) for e in entities_at_new_pos):
            return False
            
        # Remove from old position
        self.remove_entity(entity)
        
        # Update position and add to new position
        entity.x = new_x
        entity.y = new_y
        self.add_entity(entity)
        
        return True
        
    def mark_room_explored(self, room_id: int) -> None:
        """Mark a room as explored."""
        self.explored_rooms.add(room_id)
        self.game_map.mark_room_explored(room_id)
        
    def to_dict(self) -> dict:
        """Convert the state to a dictionary for serialization."""
        return {
            'game_map': self.game_map.to_dict(),
            'state_type': self.state_type.name,
            'entities': {
                f"{x},{y}": [e.to_dict() for e in entities]
                for (x, y), entities in self.entities.items()
            },
            'explored_rooms': list(self.explored_rooms),
            'turn': self.turn
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> 'GameState':
        """Create a state from a dictionary."""
        from core.entity import Entity  # Import here to avoid circular import
        
        game_map = GameMap.from_dict(data['game_map'])
        state = cls(game_map)
        state.state_type = GameStateType[data['state_type']]
        state.explored_rooms = set(data['explored_rooms'])
        state.turn = data['turn']
        
        # Reconstruct entities
        for pos_str, entity_data_list in data['entities'].items():
            x, y = map(int, pos_str.split(','))
            for entity_data in entity_data_list:
                entity = Entity.from_dict(entity_data)
                state.add_entity(entity)
                
        return state 