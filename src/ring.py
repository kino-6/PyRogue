from equipment import Equipment
from utils.assets_manager import AssetsManager
import random


class Ring(Equipment):
    def __init__(self, x=0, y=0, ring_data={}, is_cursed=False):
        super().__init__("Ring", x, y, char="=", color="white")
        self.load_data(ring_data)
        self.calc_effect()

    def load_data(self, data):
        # 指輪のデータを読み込む処理
        pass

    def calc_effect(self):
        # 指輪の効果を計算する処理
        pass

    def equip(self, character):
        super().equip(character)
        # 指輪を装備した際の特殊効果をここに実装

    def unequip(self, character):
        super().unequip(character)
        # 指輪を外した際の処理をここに実装


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
