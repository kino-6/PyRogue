import uuid
import yaml
import glob
import os
from assets_manager import AssetsManager
from weapon import WeaponManager
from armor import ArmorManager
from ring import RingManager
from item import Item
from food import Food
from potion import PotionManager


class ItemManager:
    def __init__(self, base_path=None):
        self.assets_manager = AssetsManager(base_path)
        # assets/data/item ディレクトリ
        self.item_dir = self.assets_manager.get_item_path("")
        self._items_cache = self.get_all_items_with_unique_id()

    def get_all_items_with_unique_id(self):
        items_with_id = []

        rm = RingManager()
        for ring in rm.ring_instance_list:
            item_id = str(uuid.uuid4())
            items_with_id.append({"id": item_id, "item": ring})

        wm = WeaponManager()
        for weapon in wm.weapon_instance_list:
            item_id = str(uuid.uuid4())
            items_with_id.append({"id": item_id, "item": weapon})

        am = ArmorManager()
        for armor in am.armor_instance_list:
            item_id = str(uuid.uuid4())
            items_with_id.append({"id": item_id, "item": armor})

        # ポーションの追加
        pm = PotionManager()
        for potion in pm.potion_instance_list:
            item_id = str(uuid.uuid4())
            items_with_id.append({"id": item_id, "item": potion})

        return items_with_id

    def create_item_by_id(self, item_id: str) -> Item:
        """アイテムIDからアイテムを生成する"""
        # 特殊なアイテムの処理
        if item_id.lower() == "food":
            return self.create_food()

        # 通常のアイテムの処理
        items = self._items_cache
        for item_data in items:
            if item_data["item"].name == item_id:
                return item_data["item"].copy()
        return None

    def get_all_item_names(self) -> list[str]:
        """利用可能なすべてのアイテム名のリストを返す"""
        items = self._items_cache
        return list(set(item_data["item"].name for item_data in items))

    def create_food(self) -> Food:
        """新しい食料アイテムを生成する"""
        from food import Food
        return Food()  # 内部でランダムな食料が生成される

    def create_potion(self, potion_id):
        """指定されたIDのポーションを生成する"""
        from potion import Potion
        potion_data = self.load_item_data("potion", potion_id)
        if potion_data:
            return Potion(potion_data=potion_data)
        return None
