from equipment import Equipment
from utils.assets_manager import AssetsManager
import random
class Armor(Equipment):
    def __init__(self, x=0, y=0, armor_data={}, is_cursed=False):
        super().__init__("Armor", x, y, char="]", color="white", is_cursed=is_cursed)
        self.load_data(armor_data)

    def load_data(self, data):
        if not data:
            print("Warning: Empty Armor data loaded.", data)
            return

        self.name = data.get("name", "Unknown weapon")
        self.char = data.get("char", ")")
        self.color = data.get("color", "white")
        self.undefined_name = data.get("undefined_name", "Unknown weapon")
        self.armor = data.get("armor", "0")
        self.throw_dice = data.get("throw_dice", "0d0")
        self.protection_bonus = data.get("protection_bonus", "0")
        self.avoidance_bonus = data.get("avoidance_bonus", "0")
        self.use_effect = data.get("use_effect", None)
        self.display_name = self.undefined_name

    def attach_equip_info(self):
        equip_msg = ""
        if self.is_equipped:
            equip_msg = "[E] "
        self.display_name = equip_msg + self.display_name

    def attach_curse_blessing_info(self):
        msg = ""
        if self.is_cursed:
            msg = "[C] "
        self.display_name = msg + self.display_name

    def appraisal(self):
        self.is_defined = True
        if self.protection_bonus > 0:
            self.display_name = f"{self.name} {self.armor} + {self.protection_bonus}"
        else:
            self.display_name = f"{self.name} {self.armor}"
        self.attach_curse_blessing_info()
        self.attach_equip_info()

    def calc_defense(self):
        # 防具の防御力を計算する処理
        pass

    def equip(self, character):
        super().equip(character, Armor)
        self.appraisal()

    def unequip(self, character):
        super().unequip(character)
        self.appraisal()

class ArmorManager:
    def __init__(self):
        self.load_armor_data_from_directory()

    def load_armor_data_from_directory(self) -> None:
        assets_manager = AssetsManager()
        self.armor_data_list = assets_manager.get_item_data_list("armor")

    def get_random_armor(self) -> Armor:
        if self.armor_data_list:
            armor_data = random.choice(self.armor_data_list)
            return Armor(armor_data=armor_data)
        else:
            return None
