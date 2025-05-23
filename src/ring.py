from equipment import Equipment
from assets_manager import AssetsManager
import random
from effect import *
from typing import List


class Ring(Equipment):
    def __init__(self, x=0, y=0, ring_data={}, is_cursed=False, effect=None):
        super().__init__("Ring", x, y, char="=", color="white")
        self.is_defined = False
        self.load_data(ring_data)

    def load_data(self, data):
        self.type = data.get("type", "Ring")
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
        self.undefined_name_CONST = self.undefined_name

        self.effect_name = data.get("use_effect")
        if self.effect_name in EFFECT_MAP:
            self.effect = EFFECT_MAP[self.effect_name]()
        else:
            self.effect = None

    def attach_equip_info(self):
        # [E] を装備時のみ display_name の先頭に付与
        self._equip_msg = "[E] " if self.is_equipped else ""

    def attach_curse_blessing_info(self):
        # [C] を呪い時のみ display_name の先頭に付与
        self._curse_msg = "[C] " if self.is_cursed else ""

    def not_appraisal_at_equip(self):
        # 未鑑定時は不確定名ベース
        self.attach_equip_info()
        self.attach_curse_blessing_info()
        base_name = self.name if self.is_defined else self.undefined_name_CONST
        self.display_name = f"{self._curse_msg}{self._equip_msg}{base_name}"

    def appraisal(self):
        # 鑑定時は正体名ベース
        self.is_defined = True
        self.attach_equip_info()
        self.attach_curse_blessing_info()
        base_name = self.name
        self.display_name = f"{self._curse_msg}{self._equip_msg}{base_name}"

    def equip(self, character):
        super().equip(character, Ring)
        print(f"call equip ring, {self.name}, effect: {self.effect_name} {self.effect}")
        if self.effect:
            self.effect.apply_effect(character)
        self.not_appraisal_at_equip()  # 装備時は未鑑定名で

        inventory_txt, is_defined_list = character.get_inventory_str_list()
        print(inventory_txt)

    def unequip(self, character):
        super().unequip(character)
        print(f"call unequip ring, {self.name}, {self.is_equipped}")
        if self.effect:
            self.effect.remove_effect(character)
        self.not_appraisal_at_equip()

    def __repr__(self):
        message = f"{self.name}, {self.char}, {self.effect_name}"
        message += f"{self.hit_bonus}/{self.avoidance_bonus}/{self.protection_bonus}"
        return message

    def get_info(self):
        info = []
        info.append(f"Name: {self.name if self.is_defined else self.undefined_name_CONST}")
        # info.append(f"equipment type: ring")
        info.append(f"hit: {self.hit_bonus} ")
        info.append(f"avd: {self.avoidance_bonus} ")
        info.append(f"prt: {self.protection_bonus} ")
        info.append(f"effect: {self.effect_name if self.effect_name else 'None'}")
        info.append(f"Description: {self.flavor_text}")
        return info


class RingManager:
    def __init__(self):
        self.load_ring_data_from_directory()

    def load_ring_data_from_directory(self) -> None:
        assets_manager = AssetsManager()
        self.ring_data_list = assets_manager.get_item_data_list("ring")
        self.ring_instance_list = self.get_ring_instance_list()

    def get_ring_instance_list(self) -> List[Ring]:
        ring_instance_list = []
        for ring_data in self.ring_data_list:
            ring_instance = Ring(ring_data=ring_data)
            ring_instance_list.append(ring_instance)
        return ring_instance_list

    def get_random_ring(self) -> Ring:
        if self.ring_data_list:
            data = random.choice(self.ring_data_list)
            return Ring(ring_data=data)
        else:
            print("error select ring.")
            return None

    def get_ring_by_effect(self, effect_name: str) -> Ring:
        for data in self.ring_data_list:
            if data.get("use_effect") == effect_name:
                return Ring(ring_data=data)
        print(f"error: no ring with effect {effect_name}")
        return None

    def get_ring_by_partial_name(self, name: str) -> Ring:
        """
        名前が部分一致する指輪を返す
        Args:
            name: 検索する指輪の名前（部分一致）
        Returns:
            Ring: 見つかった指輪のインスタンス、見つからない場合はNone
        """
        for data in self.ring_data_list:
            if name.lower() in data.get("name", "").lower():  # 大文字小文字を区別しない
                return Ring(ring_data=data)
        print(f"error: no ring matching name '{name}'")
        return None
