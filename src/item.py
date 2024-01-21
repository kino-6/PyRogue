from entity import Entity


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
