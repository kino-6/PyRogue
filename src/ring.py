from equipment import Equipment
from assets_manager import AssetsManager
import random
from effect import *

class Ring(Equipment):
    def __init__(self, x=0, y=0, ring_data={}, is_cursed=False, effect=None):
        super().__init__("Ring", x, y, char="=", color="white")
        self.load_data(ring_data)
        self.effect = effect

    def load_data(self, data):
        self.name = data.get("name", "Unknown Ring")
        effect_name = data.get("use_effect")
        if effect_name in EFFECT_MAP:
            self.effect = EFFECT_MAP.get(effect_name, NoEffect)()

    def equip(self, character):
        super().equip(character, "ring")
        if self.effect:
            self.effect.apply_effect(character)

    def unequip(self, character):
        if self.effect:
            self.effect.remove_effect(character)
        super().unequip(character)


class RingManager:
    def __init__(self):
        self.load_ring_data_from_directory()

    def load_ring_data_from_directory(self) -> None:
        assets_manager = AssetsManager()
        self.ring_data_list = assets_manager.get_item_data_list("ring")

    def get_random_ring(self) -> Ring:
        if self.ring_data_list:
            data = random.choice(self.ring_data_list)
            return Ring(ring_data=data)
        else:
            return None
