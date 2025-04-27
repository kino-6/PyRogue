from status import Status
from entity import Entity
from item import Item
from inventory import Inventory
import constants as const
import string
from typing import Type
from typing import Dict, Optional
from weapon import Weapon
from armor import Armor
from ring import Ring


class Character(Entity):
    def __init__(self, x, y, status: Status, logger=None):
        super().__init__(x, y, status.char, status.color)
        self.status = status
        self.logger = logger
        self.turn = 0
        self.turns_since_last_recovery = 0
        self.inventory = Inventory()
        self.equipped_weapon = None
        self.equipped_armor = None
        self.equipped_right_ring = None
        self.equipped_left_ring = None

    def get_looped_element(self, idx, looped_list):
        looped_idx = idx % len(looped_list)
        return looped_list[looped_idx]

    def get_inventory_with_key(self, item_type: Type[Item]) -> Dict[str, Optional[Item]]:
        """
        インベントリのキーに対応した特定の型のアイテムのリストを作成するメソッド

        Args:
        item_type (Type[Item]): 取得するアイテムの型

        Returns:
        Dict[str, Optional[Item]]: インベントリのキーに対応したアイテムの辞書
        """
        KEY_LIST = list(string.ascii_lowercase)
        items_by_key = {}

        for key, item in zip(KEY_LIST, self.inventory.items):
            if isinstance(item, item_type):
                items_by_key[key] = item
        return items_by_key

    def get_inventory_str_list(self):
        KEY_LIST = list(string.ascii_lowercase)
        result_str = []
        is_defined_list = []
        for i, item in enumerate(self.inventory.items):
            idx_key = self.get_looped_element(i, KEY_LIST)
            result_str.append(f"{idx_key}) {item.display_name}")
            is_defined_list.append(item.is_defined)
        return result_str, is_defined_list

    def get_char(self):
        return self.status.char

    def move(self, dx, dy, game):
        new_x, new_y = int(self.x + dx), int(self.y + dy)
        if game.is_walkable(new_x, new_y):
            self.x, self.y = new_x, new_y
            self.pick_up_item_at_feet(game)

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, damage):
        self.status.current_hp -= damage
        return self.status.current_hp <= 0

    def heal_damage(self, amount):
        # HPを回復し、最大HPを超えないようにする
        self.status.current_hp += amount
        if self.status.current_hp > self.status.max_hp:
            self.status.current_hp = self.status.max_hp

    def update_turn(self):
        self.turn += 1
        self.update_nutrition()
        self.natural_recovery()

    def sate_hunger(self, nutrition_change):
        self.status.food_left = max(0, min(self.status.food_left + nutrition_change, const.STOMACHSIZE))

    def update_nutrition(self, nutrition_change=-const.EACH_TURN_STARVE):
        self.sate_hunger(nutrition_change)
        self.check_hunger_state()

    def check_hunger_state(self):
        # 満腹度に応じた状態をチェックするロジックを実装
        pass

    def natural_recovery(self):
        recovery_amount = int(self.status.max_hp / const.RECOVERY_AMOUNT_CONF) + 1
        recovery_interval = const.RECOVERY_INTERVAL
        self.turns_since_last_recovery += 1

        # 一定ターン経過後にHPを回復
        if self.turns_since_last_recovery >= recovery_interval:
            self.heal_damage(recovery_amount)
            self.turns_since_last_recovery = 0  # ターン数をリセット

    def add_logger(self, msg: str):
        if self.logger:
            self.logger.info(msg)

    def pick_up_item_at_feet(self, game):
        item = game.get_item_at_position(self.x, self.y)
        if item:
            if len(self.inventory.items) < const.INVENTORY_MAX:
                self.inventory.add_item(item)
                game.remove_item_at_position(self.x, self.y)
                self.add_logger(f"{self.status.name} pick {item.display_name}")
            else:
                self.add_logger(f"{self.status.name} can't pick up {item.display_name}, my bags full.")

    def gain_experience(self, value):
        self.status.exp += value

    def use_item(self, item):
        item.use(self)

    def equip(self, type, equipment, position="left"):
        if type == Weapon:
            self.equipped_weapon = equipment
        elif type == Armor:
            self.equipped_armor = equipment
            if equipment:
                self.status.armor = equipment.armor
        elif type == Ring:
            if position == "left":
                if self.equipped_left_ring:
                    self.equipped_left_ring.unequip(self)
                self.equipped_left_ring = equipment
                equipment.equip(self)
