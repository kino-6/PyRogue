import yaml
import random
import glob
from equipment import Equipment
from assets_manager import AssetsManager


class Weapon(Equipment):
    def __init__(self, x=0, y=0, weapon_data={}, is_cursed=False):
        super().__init__("Weapon", x, y, char=")", color="white", is_cursed=is_cursed)
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
        self.flavor_text = data.get("flavor_text", "")
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
        if self.dmg_bonus > 0:
            self.display_name = f"{self.name} {self.wielded_dice} + {self.dmg_bonus}"
        else:
            self.display_name = f"{self.name} {self.wielded_dice}"
        self.attach_curse_blessing_info()
        self.attach_equip_info()

    def __repr__(self):
        message = f"{self.name}, {self.char}, {self.wielded_dice}"
        return message

    def calc_damage(self):
        # 武器のダメージを計算する処理
        pass

    def equip(self, character):
        super().equip(character, Weapon)
        self.appraisal()
        # print("equip ", self.display_name)

    def unequip(self, character):
        super().unequip(character)
        self.appraisal()
        # print("unequip ", self.display_name)

    def get_info(self):
        info = []
        info.append(f"Name: {self.name if self.is_defined else self.undefined_name}")
        # info.append(f"種類: 武器")
        info.append(f"pow: {self.wielded_dice}")
        info.append(f"bonus: {self.dmg_bonus}")
        info.append(f"hit: {self.hit_bonus}")
        info.append(f"effect: {self.use_effect if self.use_effect else 'なし'}")
        info.append(f"Description: {self.flavor_text}")
        return "\n".join(info)


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
