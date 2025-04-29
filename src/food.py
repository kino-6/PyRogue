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

        with open(food_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
            self.food_data = data
            self.name = random.choice(data.get("food_names", ["Food"]))
            self.char = data.get("char", ":")
            self.color = data.get("color", "brown")
            self.undefined_name = data.get("undefined_name", "Unknown Food")
            self.nutrition_base = data.get("nutrition_base", const.HUNGERTIME)
            self.nutrition_tune = data.get("nutrition_tune", const.FOOD_TUNE_VALUE)
            self.nutrition_rand_max = data.get("nutrition_rand_max", const.FOOD_RAND_MAX)
            self.display_name = self.undefined_name
            self.is_defined = False

    def calc_nutrition(self):
        """満腹度の計算"""
        self.nutrition = self.nutrition_base - self.nutrition_tune + random.randint(0, self.nutrition_rand_max)

    def get_nutrition_percent(self):
        """満腹度を百分率で返す"""
        # HUNGERTIME（最大満腹度）を100%として計算
        return int((self.nutrition / const.STOMACHSIZE) * 100)

    def use(self, character: Character):
        character.sate_hunger(self.nutrition)
        
    def appraisal(self):
        """鑑定時の処理"""
        self.is_defined = True
        # 満腹度をパーセント表示に変更
        self.display_name = f"{self.name} ({self.get_nutrition_percent()}%)"

    def get_info(self):
        """アイテム情報の取得"""
        info = []
        info.append(f"Name: {self.name if self.is_defined else self.undefined_name}")
        if self.is_defined:
            info.append(f"Nutrition: {self.get_nutrition_percent()}%")
        info.append(f"Description: {self.food_data.get('flavor_text', '')}")
        return "\n".join(info)
