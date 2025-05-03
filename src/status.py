import yaml
import constants as const


class Status:
    def __init__(self, data: dict):
        self.name = data.get("name", "Unknown")
        self.char = data.get("char", "?")
        self.color = data.get("color", "white")
        self.level = data.get("level", 1)
        self.max_hp = data.get("max_hp", 10)
        self.current_hp = self.max_hp
        self.strength = data.get("strength", 1)
        self.armor = data.get("armor", 0)
        self.exp = data.get("exp", 0)
        self.exp_level = data.get("exp_level", 1)
        self.next_exp = 0
        self.gold = data.get("gold", 0)
        self.food_left = data.get("food_left", const.STOMACHSIZE)
        self.based_hit_rate = data.get("based_hit_rate", const.BASED_HIT_RATE)
        
        # ダイス情報の追加
        self.dice_sides = data.get("dice_sides", 4)  # デフォルトは4面ダイス
        self.dice_count = data.get("dice_count", 1)  # デフォルトは1個

        # calc
        self.attack_power = self.strength
        self.defense_power = self.armor
        self.chase_power = data.get("chase_power", 0)

    def __repr__(self):
        message = f"{self.name}: {self.current_hp}/{self.max_hp}"
        return message

    def generate_status_txt(self, x=0, y=0):
        """generate main UI status txt list"""
        status_txt = [
            f"Name: {self.name}, ({x}, {y})",
            f"Floor: {self.level}",
            f"Gold: {self.gold}",
            f"Hp: {self.current_hp}/{self.max_hp}",
            f"Str: {self.strength}",
            f"Ac: {self.armor}",
            f"ExpLv: {self.exp_level}",
            f"Exp: {self.exp} / {self.next_exp}",
            f"Food: {int((self.food_left / const.STOMACHSIZE)*100)} %",
        ]
        return status_txt

    def copy(self):
        """ステータスの深いコピーを作成"""
        data = {
            "char": self.char,
            "name": self.name,
            "max_hp": self.max_hp,
            "strength": self.strength,
            "exp": self.exp,
            "level": self.level,
            "armor": self.armor,
            "color": self.color,
            "exp_level": self.exp_level,
            "chase_power": self.chase_power,
            "dice_sides": self.dice_sides,
            "dice_count": self.dice_count
        }
        return Status(data)
