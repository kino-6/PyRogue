from item import Item


class Equipment(Item):
    def __init__(self, name, x=0, y=0, char="e", color="white", undefined_name="", is_cursed=False):
        super().__init__(name, x, y, char, color, undefined_name)
        self.is_equipped = False
        self.is_cursed = is_cursed

    def define_position(self, character):
        position = "left"
        if character.equipped_left_ring:
            position = "right"
        return position

    def equip(self, character, type):
        self.is_equipped = True
        position = self.define_position(character)
        character.equip(type, self, position)
        pass

    def unequip(self, character):
        self.is_equipped = False
        position = self.define_position(character)
        character.equip(type, None, position)
        pass
