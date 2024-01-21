from item import Item
from character import Character


class Equipment(Item):
    def __init__(self, name, x=0, y=0, char="e", color="white", undefined_name=""):
        super().__init__(name, x, y, char, color, undefined_name)
        self.is_equipped = False

    def equip(self, character: Character):
        # 装備する際の処理をここに実装します。
        self.is_equipped = True
        pass

    def unequip(self, character: Character):
        # 装備を外す際の処理をここに実装します。
        self.is_equipped = False
        pass
