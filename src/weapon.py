import yaml
import random
import glob
from equipment import Equipment
from character import Character
from utils.assets_manager import AssetsManager


class Weapon(Equipment):
    def __init__(self, x=0, y=0, weapon_data={}):
        super().__init__("Weapon", x, y, char=")", color="white")
        self.load_data(weapon_data)

    def load_data(self, data):
        if not data:
            print("Warning: Empty weapon data loaded.", data)
            return

        self.name = data.get("name", "Unknown weapon")
        self.char = data.get("char", ")")
        self.color = data.get("color", "white")
        self.undefined_name = data.get("undefined_name", "Unknown weapon")
        self.wielded_dice = data.get("wielded_dice", "0d0")
        self.throw_dice = data.get("throw_dice", "0d0")
        self.dmg_bonus = data.get("dmg_bonus", "0")
        self.hit_bonus = data.get("hit_bonus", "0")
        self.use_effect = data.get("use_effect", None)

    def __repr__(self):
        message = f"{self.name}, {self.char}, {self.wielded_dice}"
        return message

    def calc_damage(self):
        # 武器のダメージを計算する処理
        pass

    def equip(self, character: Character):
        super().equip(character)
        # 武器を装備した際の効果、例えば攻撃力の増加などをここに実装

    def unequip(self, character: Character):
        super().unequip(character)
        # 武器を外した際の処理をここに実装


class WeaponManager:
    def __init__(self):
        self.load_weapon_data_from_directory()

    def load_weapon_data_from_directory(self) -> None:
        assets_manager = AssetsManager()
        self.weapon_data_list = assets_manager.get_item_data_list("weapon")

    def get_random_weapon(self) -> Weapon:
        if self.weapon_data_list:
            weapon_data = random.choice(self.weapon_data_list)
            return Weapon(weapon_data=weapon_data)
        else:
            return None
