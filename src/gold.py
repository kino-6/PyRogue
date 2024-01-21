from entity import Entity
import random


class Gold(Entity):
    def __init__(self, x=0, y=0, amount=0):
        super().__init__(x, y, "*", "darkgoldenrod2")
        self.amount = amount

    def determine_gold_amount(self, current_level):
        self.amount = random.randint(0, 50 + 10 * current_level) + random.randint(1, 3)
