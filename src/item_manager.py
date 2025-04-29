import uuid
import yaml
import glob
import os
from assets_manager import AssetsManager
from weapon import WeaponManager
from armor import ArmorManager
from ring import RingManager
from item import Item


class ItemManager:
    def __init__(self, base_path=None):
        self.assets_manager = AssetsManager(base_path)
        # assets/data/item ディレクトリ
        self.item_dir = self.assets_manager.get_item_path("")

    def get_all_items_with_unique_id(self):
        items_with_id = []

        # wm = WeaponManager()
        # for weapon in wm.weapon_instance_list:
        #     item_id = str(uuid.uuid4())
        #     items_with_id.append({"id": item_id, "item": weapon})

        # am = ArmorManager()
        # for armor in am.armor_instance_list:
        #     item_id = str(uuid.uuid4())
        #     items_with_id.append({"id": item_id, "item": armor})

        rm = RingManager()
        for ring in rm.ring_instance_list:
            item_id = str(uuid.uuid4())
            items_with_id.append({"id": item_id, "item": ring})

        return items_with_id
