from entity import Entity
import os
import yaml


class Item(Entity):
    def __init__(self, name, x=0, y=0, char="a", color="white", undefined_name="", display_name=""):
        super().__init__(x, y, char, color)
        self.name = name
        self.undefined_name = undefined_name
        self.display_name = display_name
        self.is_defined = False

    def appraisal(self):
        # override
        pass

    def use(self, character):
        pass  # このメソッドはサブクラスでオーバーライドされるべきです。

    def equip(self, character):
        pass  # 装備可能なアイテムの場合にオーバーライドします。

    @classmethod
    def from_dict(cls, data):
        # nameは必須
        name = data.get("name", "")
        type = data.get("type", "Item")
        x = data.get("x", 0)
        y = data.get("y", 0)
        char = data.get("char", "a")
        color = data.get("color", "white")
        undefined_name = data.get("undefined_name", "")
        display_name = data.get("display_name", "")

        item = cls(name, x, y, char, color, undefined_name, display_name)
        # その他の属性もセット
        for k, v in data.items():
            if not hasattr(item, k):
                setattr(item, k, v)
        return item
