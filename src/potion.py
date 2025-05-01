from item import Item
from effect import StrengthEffect, RegenerationEffect, ProtectionEffect, FullRestorationEffect, InvisibilityEffect
import random

class Potion(Item):
    def __init__(self, x=0, y=0, potion_data={}):
        super().__init__("Potion", x, y, char="!", color="white")
        self.load_data(potion_data)

    def load_data(self, data):
        if not data:
            return

        self.type = data.get("type", "Potion")
        self.name = data.get("name", "Unknown potion")
        self.char = data.get("char", "!")
        self.color = data.get("color", "white")
        self.undefined_name = data.get("undefined_name", "Unknown potion")
        self.effect_type = data.get("effect", None)
        self.effect_duration = data.get("duration", 0)
        self.flavor_text = data.get("flavor_text", "")
        self.display_name = self.undefined_name

    def use(self, character):
        """ポーションを使用する"""
        if self.effect_type == "strength":
            effect = StrengthEffect()
        elif self.effect_type == "regeneration":
            effect = RegenerationEffect(duration=self.effect_duration)
        elif self.effect_type == "protection":
            effect = ProtectionEffect()
        elif self.effect_type == "full_restoration":
            effect = FullRestorationEffect()
        elif self.effect_type == "invisibility":
            effect = InvisibilityEffect(duration=self.effect_duration)
        else:
            return

        effect.apply_effect(character)
        character.add_logger(f"You drink the {self.name}.")

    def appraisal(self):
        """鑑定時の処理"""
        self.is_defined = True
        self.display_name = self.name

import random
from potion import Potion
from assets_manager import AssetsManager
from typing import List

class PotionManager:
    def __init__(self):
        self.load_potion_data_from_directory()

    def load_potion_data_from_directory(self) -> None:
        assets_manager = AssetsManager()
        self.potion_data_list = assets_manager.get_item_data_list("potion")
        self.potion_instance_list = self.get_potion_instance_list()

    def get_potion_instance_list(self) -> List[Potion]:
        potion_instance_list = []
        for potion_data in self.potion_data_list:
            potion_instance = Potion(potion_data=potion_data)
            potion_instance_list.append(potion_instance)
        return potion_instance_list

    def get_random_potion(self) -> Potion:
        if self.potion_data_list:
            data = random.choice(self.potion_data_list)
            return Potion(potion_data=data)
        else:
            print("error select potion.")
            return None
