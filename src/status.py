import yaml
import constants as const


class Status:
    def __init__(self, data: dict):
        self.char = data["char"]
        self.name = data["name"]
        self.max_hp = data["max_hp"]
        self.strength = data["strength"]
        self.exp = data["exp"]
        self.level = data["level"]
        self.armor = data["armor"]
        self.color = data["color"]
        self.exp_level = data["exp_level"]

        # calc
        self.current_hp = self.max_hp
        self.gold = 0
        self.next_exp = 10
        self.food_left = const.STOMACHSIZE

        # todo + wired wepon
        self.attack_power = self.strength
        self.defense_power = self.armor
        self.based_hit_rate = const.BASED_HIT_RATE

    def generate_status_txt(self):
        """generate main UI status txt list"""
        status_txt = [
            f"Name: {self.name}",
            f"Level: {self.level}",
            f"Gold: {self.gold}",
            f"Hp: {self.current_hp}/{self.max_hp}",
            f"Str: {self.strength}",
            f"Ac: {self.armor}",
            f"ExpLv: {self.exp_level}",
            f"Exp: {self.exp}",
            f"Food: {int((self.food_left / const.STOMACHSIZE)*100)} %",
        ]
        return status_txt
