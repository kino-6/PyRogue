import yaml
import random
from item import Item
from entity import Entity
from character import Character
import constants as const
from assets_manager import AssetsManager


class Food(Item):
    def __init__(self, x=0, y=0):
        super().__init__("Food", x, y, ":", "white")
        self.load_data()
        self.calc_nutrition()

    def load_data(self):
        assets_manager = AssetsManager()
        directory = assets_manager.get_item_path("food")
        food_path = directory / "food.yaml"

        with open(food_path, "r") as file:
            data = yaml.safe_load(file)
            self.name = data.get("name", "Food")
            self.char = data.get("char", ":")
            self.color = data.get("color", "brown")
            self.undefined_name = data.get("undefined_name", "Unknown Food")
            self.nutrition_base = data.get("nutrition_base", const.HUNGERTIME)
            self.nutrition_tune = data.get("nutrition_tune", const.FOOD_TUNE_VALUE)
            self.nutrition_rand_max = data.get("nutrition_rand_max", const.FOOD_RAND_MAX)
            self.display_name = self.undefined_name

    def calc_nutrition(self):
        self.nutrition = self.nutrition_base - self.nutrition_tune + random.randint(0, self.nutrition_rand_max)

    def use(self, character: Character):
        character.sate_hunger(self.nutrition)
