from typing import Dict, Optional, List
from core.entity import Entity
from dataclasses import dataclass

@dataclass
class CharacterStatus:
    """Character status information."""
    name: str
    max_hp: int
    current_hp: int = None  # Will be set to max_hp if None
    attack: int = 0
    defense: int = 0
    gold: int = 0
    experience: int = 0
    level: int = 1
    turn: int = 0  # Add turn counter
    food_left: int = 0
    next_level_exp: int = 0
    
    def __post_init__(self):
        if self.current_hp is None:
            self.current_hp = self.max_hp

class Character(Entity):
    """Represents a character in the game."""
    
    def __init__(self, x: int, y: int, name: str, char: str, status: CharacterStatus):
        super().__init__(x, y, name, char)
        self.status = status
        self.inventory: List[Entity] = []  # Inventory list
        
    @property
    def is_alive(self) -> bool:
        return self.status.current_hp > 0
        
    def take_damage(self, amount: int) -> int:
        """Take damage and return the actual amount of damage taken."""
        actual_damage = max(1, amount - self.status.defense)
        self.status.current_hp = max(0, self.status.current_hp - actual_damage)
        return actual_damage
        
    def heal(self, amount: int) -> int:
        """Heal and return the actual amount healed."""
        if not self.is_alive:
            return 0
        old_hp = self.status.current_hp
        self.status.current_hp = min(self.status.max_hp, self.status.current_hp + amount)
        return self.status.current_hp - old_hp
        
    def gain_experience(self, amount: int) -> bool:
        """Gain experience and return True if leveled up."""
        self.status.experience += amount
        # Simple leveling formula: need 100 * level experience points to level up
        needed_exp = 100 * self.status.level
        if self.status.experience >= needed_exp:
            self.status.level += 1
            self.status.max_hp += 5
            self.status.attack += 2
            self.status.defense += 1
            self.status.current_hp = self.status.max_hp  # Full heal on level up
            self.status.experience -= needed_exp
            return True
        return False
        
    def get_inventory_lines(self) -> List[str]:
        """Return a list of strings for inventory display."""
        lines = []
        for idx, item in enumerate(self.inventory):
            # Example: a) [E] Short Sword 2d4 + 1
            key = chr(ord('a') + idx)
            equipped = getattr(item, 'equipped', False)
            line = f"{key}) {'[E] ' if equipped else ''}{item.display_name}"
            lines.append(line)
        return lines
        
    def to_dict(self) -> dict:
        """Convert character to dictionary for serialization."""
        base_dict = super().to_dict()
        base_dict.update({
            'status': {
                'name': self.status.name,
                'max_hp': self.status.max_hp,
                'current_hp': self.status.current_hp,
                'attack': self.status.attack,
                'defense': self.status.defense,
                'gold': self.status.gold,
                'experience': self.status.experience,
                'level': self.status.level
            }
        })
        return base_dict
        
    @classmethod
    def from_dict(cls, data: dict) -> 'Character':
        """Create character from dictionary."""
        status_data = data.pop('status')
        status = CharacterStatus(**status_data)
        return cls(data['x'], data['y'], data['name'], data['char'], status) 