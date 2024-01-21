from equipment import Equipment
from utils.assets_manager import AssetsManager


class Armor(Equipment):
    def __init__(self, x=0, y=0):
        super().__init__("Armor", x, y, char="]", color="white")
        self.load_data()
        self.calc_defense()

    def load_data(self):
        # 防具のデータを読み込む処理
        pass

    def calc_defense(self):
        # 防具の防御力を計算する処理
        pass

    def equip(self, character):
        super().equip(character)
        # 防具を装備した際の効果、例えば防御力の増加などをここに実装

    def unequip(self, character):
        super().unequip(character)
        # 防具を外した際の処理をここに実装
