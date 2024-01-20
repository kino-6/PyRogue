from item import Item
from character import Character
import utils.constants as const
import random


class Food(Item):
    def __init__(self, x=0, y=0, name="Food", nutrition=0):
        super().__init__(name, x, y, ":", color="brown")
        self.calc_nutrition()

    def calc_nutrition(self):
        self.nutrition = const.HUNGERTIME - const.FOOD_TUNE_VALUE + random.randint(0, const.FOOD_RAND_MAX)

    def use(self, character: Character):
        character.sate_hunger(self.nutrition)
