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
        self.char = data.get("char", "=")
        self.color = data.get("color", "white")
        self.undefined_name = data.get("undefined_name", "Unknown Ring")
        self.armor = data.get("armor", 0)
        self.throw_dice = data.get("throw_dice", "0d0")
        self.use_effect = data.get("use_effect", None)
        self.protection_bonus = data.get("protection_bonus", 0)
        self.avoidance_bonus = data.get("avoidance_bonus", 0)
        self.dmg_bonus = data.get("dmg_bonus", 0)
        self.hit_bonus = data.get("hit_bonus", 0)
        self.flavor_text = data.get("flavor_text", "")
        self.display_name = self.undefined_name

        self.effect_name = data.get("use_effect")
        if self.effect_name in EFFECT_MAP:
            self.effect = EFFECT_MAP[self.effect_name]()
            # self.effect = EFFECT_MAP.get(self.effect_name, NoEffect)()

    def attach_equip_info(self):
        equip_msg = ""
        if self.is_equipped:
            equip_msg = "[E] "
        # self.display_name = equip_msg + self.undefined_name
        self.display_name = equip_msg + self.display_name + "++++++++++++++++++++++++++"
        print("msg: ", equip_msg, ", is_equipped: ", self.is_equipped, "display: ", self.display_name)

    def attach_curse_blessing_info(self):
        msg = ""
        if self.is_cursed:
            msg = "[C] "
        self.display_name = msg + self.undefined_name

    def attach_judgement_info(self):
        self.undefined_name = self.name

    def appraisal_at_equip(self):
        self.attach_equip_info()
        self.attach_curse_blessing_info()

    def appraisal_at_judgment(self):
        self.attach_judgement_info()
        self.attach_equip_info()
        self.attach_curse_blessing_info()

    def equip(self, character):
        super().equip(character, Ring)
        print(f"call equip ring, {self.name}, effect: {self.effect_name} {self.effect}")
        if self.effect:
            self.effect.apply_effect(character)  # not working
        self.appraisal_at_equip()

        inventory_txt, is_defined_list = character.get_inventory_str_list()
        print(inventory_txt)

    def unequip(self, character):
        super().unequip(character)
        print(f"call unequip ring, {self.name}, {self.is_equipped}")
        if self.effect:
            self.effect.remove_effect(character)
        self.appraisal_at_equip()


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
            print("error select ring.")
            return None
