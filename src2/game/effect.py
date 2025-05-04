from typing import Dict, Optional, Callable
from game.character import Character

class Effect:
    """Base class for all effects in the game."""
    
    def __init__(self, name: str, duration: int):
        self.name = name
        self.duration = duration
        
    def apply(self, character: Character) -> None:
        """Apply the effect to a character."""
        raise NotImplementedError("Subclasses must implement apply()")
        
    def remove(self, character: Character) -> None:
        """Remove the effect from a character."""
        raise NotImplementedError("Subclasses must implement remove()")
        
    def update(self, character: Character) -> None:
        """Update the effect on a character."""
        pass

class StatModifierEffect(Effect):
    """Effect that modifies a character's stats."""
    
    def __init__(self, name: str, duration: int, stat_name: str, modifier: int):
        super().__init__(name, duration)
        self.stat_name = stat_name
        self.modifier = modifier
        self.applied = False
        
    def apply(self, character: Character) -> None:
        """Apply the stat modifier."""
        if not self.applied:
            current_value = getattr(character.status, self.stat_name)
            setattr(character.status, self.stat_name, current_value + self.modifier)
            self.applied = True
            
    def remove(self, character: Character) -> None:
        """Remove the stat modifier."""
        if self.applied:
            current_value = getattr(character.status, self.stat_name)
            setattr(character.status, self.stat_name, current_value - self.modifier)
            self.applied = False

class DamageOverTimeEffect(Effect):
    """Effect that deals damage over time."""
    
    def __init__(self, name: str, duration: int, damage_per_turn: int):
        super().__init__(name, duration)
        self.damage_per_turn = damage_per_turn
        
    def apply(self, character: Character) -> None:
        """Apply the damage over time effect."""
        pass
        
    def remove(self, character: Character) -> None:
        """Remove the damage over time effect."""
        pass
        
    def update(self, character: Character) -> None:
        """Deal damage each turn."""
        if character.is_alive():
            character.status.take_damage(self.damage_per_turn)

class HealOverTimeEffect(Effect):
    """Effect that heals over time."""
    
    def __init__(self, name: str, duration: int, heal_per_turn: int):
        super().__init__(name, duration)
        self.heal_per_turn = heal_per_turn
        
    def apply(self, character: Character) -> None:
        """Apply the heal over time effect."""
        pass
        
    def remove(self, character: Character) -> None:
        """Remove the heal over time effect."""
        pass
        
    def update(self, character: Character) -> None:
        """Heal each turn."""
        if character.is_alive():
            character.status.heal(self.heal_per_turn)

class EffectManager:
    """Manages the creation and application of effects."""
    
    def __init__(self):
        self.effect_types: Dict[str, Type[Effect]] = {
            'strength_buff': lambda d: StatModifierEffect('Strength Buff', d, 'strength', 2),
            'defense_buff': lambda d: StatModifierEffect('Defense Buff', d, 'defense', 2),
            'poison': lambda d: DamageOverTimeEffect('Poison', d, 1),
            'regeneration': lambda d: HealOverTimeEffect('Regeneration', d, 1)
        }
        
    def create_effect(self, effect_name: str, duration: int) -> Optional[Effect]:
        """Create an effect by name."""
        if effect_name in self.effect_types:
            return self.effect_types[effect_name](duration)
        return None
        
    def apply_effect(self, character: Character, effect_name: str, duration: int) -> bool:
        """Apply an effect to a character."""
        effect = self.create_effect(effect_name, duration)
        if effect:
            effect.apply(character)
            character.add_effect(effect_name, duration)
            return True
        return False 