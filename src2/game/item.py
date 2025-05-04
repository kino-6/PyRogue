from typing import Dict, Optional, List, Type
from core.entity import Entity
from game.character import Character

class Item(Entity):
    """Base class for all items in the game."""
    
    def __init__(self, x: int, y: int, name: str, display_name: str):
        super().__init__(x, y, name, display_name)
        self.identified = False
        
    def use(self, character: Character) -> bool:
        """Use the item on a character. Returns True if successful."""
        raise NotImplementedError("Subclasses must implement use()")
        
    def identify(self) -> None:
        """Identify the item."""
        self.identified = True
        
    def to_dict(self) -> dict:
        """Convert item to dictionary for serialization."""
        data = super().to_dict()
        data['identified'] = self.identified
        return data
        
    @classmethod
    def from_dict(cls, data: dict) -> 'Item':
        """Create item from dictionary."""
        item = cls(
            x=data['x'],
            y=data['y'],
            name=data['name'],
            display_name=data['display_name']
        )
        item.identified = data.get('identified', False)
        return item

class Weapon(Item):
    """Represents a weapon that can be equipped."""
    
    def __init__(self, x: int, y: int, name: str, display_name: str, damage_dice: str):
        super().__init__(x, y, name, display_name)
        self.damage_dice = damage_dice
        self.equipped = False
        
    def use(self, character: Character) -> bool:
        """Equip the weapon."""
        if self.equipped:
            return False
            
        self.equipped = True
        character.set_property('equipped_weapon', self)
        return True
        
    def unequip(self, character: Character) -> None:
        """Unequip the weapon."""
        self.equipped = False
        character.set_property('equipped_weapon', None)
        
    def to_dict(self) -> dict:
        """Convert weapon to dictionary for serialization."""
        data = super().to_dict()
        data.update({
            'damage_dice': self.damage_dice,
            'equipped': self.equipped
        })
        return data
        
    @classmethod
    def from_dict(cls, data: dict) -> 'Weapon':
        """Create weapon from dictionary."""
        weapon = cls(
            x=data['x'],
            y=data['y'],
            name=data['name'],
            display_name=data['display_name'],
            damage_dice=data['damage_dice']
        )
        weapon.identified = data.get('identified', False)
        weapon.equipped = data.get('equipped', False)
        return weapon

class Armor(Item):
    """Represents armor that can be equipped."""
    
    def __init__(self, x: int, y: int, name: str, display_name: str, defense_bonus: int):
        super().__init__(x, y, name, display_name)
        self.defense_bonus = defense_bonus
        self.equipped = False
        
    def use(self, character: Character) -> bool:
        """Equip the armor."""
        if self.equipped:
            return False
            
        self.equipped = True
        character.set_property('equipped_armor', self)
        return True
        
    def unequip(self, character: Character) -> None:
        """Unequip the armor."""
        self.equipped = False
        character.set_property('equipped_armor', None)
        
    def to_dict(self) -> dict:
        """Convert armor to dictionary for serialization."""
        data = super().to_dict()
        data.update({
            'defense_bonus': self.defense_bonus,
            'equipped': self.equipped
        })
        return data
        
    @classmethod
    def from_dict(cls, data: dict) -> 'Armor':
        """Create armor from dictionary."""
        armor = cls(
            x=data['x'],
            y=data['y'],
            name=data['name'],
            display_name=data['display_name'],
            defense_bonus=data['defense_bonus']
        )
        armor.identified = data.get('identified', False)
        armor.equipped = data.get('equipped', False)
        return armor

class Potion(Item):
    """Represents a potion that can be consumed."""
    
    def __init__(self, x: int, y: int, name: str, display_name: str, effect_name: str, duration: int):
        super().__init__(x, y, name, display_name)
        self.effect_name = effect_name
        self.duration = duration
        
    def use(self, character: Character) -> bool:
        """Consume the potion."""
        character.add_effect(self.effect_name, self.duration)
        return True
        
    def to_dict(self) -> dict:
        """Convert potion to dictionary for serialization."""
        data = super().to_dict()
        data.update({
            'effect_name': self.effect_name,
            'duration': self.duration
        })
        return data
        
    @classmethod
    def from_dict(cls, data: dict) -> 'Potion':
        """Create potion from dictionary."""
        potion = cls(
            x=data['x'],
            y=data['y'],
            name=data['name'],
            display_name=data['display_name'],
            effect_name=data['effect_name'],
            duration=data['duration']
        )
        potion.identified = data.get('identified', False)
        return potion 