from item import Item
from effect import StrengthEffect, RegenerationEffect, ProtectionEffect, FullRestorationEffect, InvisibilityEffect
import random

class Potion(Item):
    def __init__(self, x=0, y=0, potion_data={}):
        super().__init__("Potion", x, y, char="!", color="white")
        self.load_data(potion_data)
        self.potion_manager = None  # PotionManagerの参照を保持

    def load_data(self, data):
        if not data:
            print("Warning: Empty potion data loaded.", data)
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
        self.is_defined = False  # 初期状態は不確定

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

        # 使用前に鑑定状態を更新
        self.appraisal()
        # インベントリ内の同じ種類のポーションも更新
        for item in character.inventory.items:
            if isinstance(item, Potion) and item.name == self.name:
                item.is_defined = True
                item.display_name = item.name
        effect.apply_effect(character)
        character.add_logger(f"You drink the {self.name}.")

    def set_potion_manager(self, manager):
        """PotionManagerの参照を設定"""
        self.potion_manager = manager

    def appraisal(self):
        """鑑定時の処理"""
        if not self.is_defined:  # 未鑑定の場合のみ処理
            self.is_defined = True
            self.display_name = self.name
            if self.potion_manager:
                self.potion_manager.mark_as_identified(self.name)
                # インベントリ内の同じ種類のポーションも更新
                for item in self.potion_manager.potion_instance_list:
                    if item.name == self.name:
                        item.is_defined = True
                        item.display_name = item.name

    def get_info(self):
        info = []
        info.append(f"Name: {self.name if self.is_defined else self.undefined_name}")
        info.append(f"Effect: {self.effect_type if self.is_defined else 'Unknown'}")
        if self.is_defined and self.effect_duration > 0:
            info.append(f"Duration: {self.effect_duration}")
        info.append(f"Description: {self.flavor_text}")
        return "\n".join(info)

    def __repr__(self):
        return f"{self.name if self.is_defined else self.undefined_name}"

import random
from potion import Potion
from assets_manager import AssetsManager
from typing import List

class PotionManager:
    def __init__(self):
        self.undefined_names = [
            "Mysterious potion",
            "Strange potion",
            "Unusual potion",
            "Curious potion",
            "Enigmatic potion",
            "Puzzling potion",
            "Bizarre potion",
            "Odd potion",
            "Weird potion",
            "Eerie potion"
        ]
        self.identified_potions = set()  # 鑑定済みのポーション名を保持
        self.potion_undefined_names = {}  # ポーションの種類ごとの不確定名称を保持
        self.load_potion_data_from_directory()

    def load_potion_data_from_directory(self) -> None:
        assets_manager = AssetsManager()
        self.potion_data_list = assets_manager.get_item_data_list("potion")
        # ポーションの種類ごとに不確定名称を割り当て
        used_names = set()  # 使用済みの不確定名称を追跡
        for potion_data in self.potion_data_list:
            if potion_data["name"] not in self.potion_undefined_names:
                # 未使用の不確定名称を選択
                available_names = [name for name in self.undefined_names if name not in used_names]
                if not available_names:
                    # すべての名称が使用済みの場合は、最初からやり直す
                    used_names.clear()
                    available_names = self.undefined_names
                selected_name = random.choice(available_names)
                used_names.add(selected_name)
                self.potion_undefined_names[potion_data["name"]] = selected_name
        self.potion_instance_list = self.get_potion_instance_list()

    def get_potion_instance_list(self) -> List[Potion]:
        potion_instance_list = []
        for potion_data in self.potion_data_list:
            potion_instance = Potion(potion_data=potion_data)
            potion_instance.set_potion_manager(self)  # PotionManagerの参照を設定
            # ポーションの種類ごとに固定された不確定名称を割り当て
            potion_instance.undefined_name = self.potion_undefined_names[potion_data["name"]]
            potion_instance.display_name = potion_instance.undefined_name
            # 鑑定済みの場合は真の名称を表示
            if potion_instance.name in self.identified_potions:
                potion_instance.is_defined = True
                potion_instance.display_name = potion_instance.name
            potion_instance_list.append(potion_instance)
        return potion_instance_list

    def get_random_potion(self) -> Potion:
        if self.potion_data_list:
            data = random.choice(self.potion_data_list)
            potion = Potion(potion_data=data)
            potion.set_potion_manager(self)  # PotionManagerの参照を設定
            # ポーションの種類ごとに固定された不確定名称を割り当て
            potion.undefined_name = self.potion_undefined_names[data["name"]]
            potion.display_name = potion.undefined_name
            # 鑑定済みの場合は真の名称を表示
            if potion.name in self.identified_potions:
                potion.is_defined = True
                potion.display_name = potion.name
            return potion
        else:
            print("error select potion.")
            return None

    def mark_as_identified(self, potion_name: str) -> None:
        """ポーションを鑑定済みとしてマークする"""
        self.identified_potions.add(potion_name)
        # 既存のポーションインスタンスの表示名を更新
        for potion in self.potion_instance_list:
            if potion.name == potion_name:
                potion.is_defined = True
                potion.display_name = potion.name

    def update_inventory_potions(self, inventory_items: List[Item]) -> None:
        """インベントリ内のポーションの表示名を更新する"""
        for item in inventory_items:
            if isinstance(item, Potion) and item.name in self.identified_potions:
                item.is_defined = True
                item.display_name = item.name
