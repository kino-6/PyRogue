class SpecialEffect:
    def apply_effect(self, character):
        pass

    def remove_effect(self, character):
        pass

class StrengthEffect(SpecialEffect):
    def apply_effect(self, character):
        character.damage_bonus += 5
        character.hit_bonus += 1

    def remove_effect(self, character):
        character.damage_bonus -= 5
        character.hit_bonus -= 1

class NoEffect(SpecialEffect):
    def apply_effect(self, character):
        pass

    def remove_effect(self, character):
        pass


EFFECT_MAP = {
    "no_effect": NoEffect,
    "add_strength": StrengthEffect,
}
