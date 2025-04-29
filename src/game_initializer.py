import yaml
from player import Player
from status import Status
from stair import Stairs
from enemy import EnemyManager
from assets_manager import AssetsManager


class GameInitializer:
    def __init__(self, game, logger):
        self.game = game
        self.logger = logger
        self.assets_manager = AssetsManager()

    def new_player(self):
        yaml_file = self.assets_manager.get_chara_path("player.yaml")
        with open(yaml_file, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
        
        # ステータスの設定
        player_status = Status(data)
        player = Player(0, 0, player_status, self.logger)

        # 初期装備の設定
        if "initial_equipment" in data:
            from item_manager import ItemManager
            item_manager = ItemManager()
            
            # 武器
            if "weapon" in data["initial_equipment"]:
                weapon = item_manager.create_item_by_id(data["initial_equipment"]["weapon"])
                print(f"init weapon: {weapon=}")
                if weapon:
                    player.inventory.add_item(weapon)
                    weapon.equip(player)
            
            # 防具
            if "armor" in data["initial_equipment"]:
                armor = item_manager.create_item_by_id(data["initial_equipment"]["armor"])
                if armor:
                    player.inventory.add_item(armor)
                    armor.equip(player)
            
            # Food
            if "food" in data["initial_equipment"]:
                for one_food in data["initial_equipment"]["food"]:
                    food = item_manager.create_item_by_id(one_food)
                    if food:
                        food.appraisal()
                        player.inventory.add_item(food)

            # その他のアイテム
            if "items" in data["initial_equipment"]:
                for item_id in data["initial_equipment"]["items"]:
                    item = item_manager.create_item_by_id(item_id)
                    if item:
                        player.inventory.add_item(item)

        return player

    def setup_player(self):
        player = self.new_player()
        self.game.teleport_entity(player)
        self.game.add_entity(player)
        return player

    def setup_stairs(self):
        stair = Stairs()
        self.game.teleport_entity(stair)
        self.game.add_entity(stair)
        return stair

    def setup_enemies(self, level, number_of_enemies):
        enemy_manager = EnemyManager()
        enemy_manager.create_enemies(self.game, level, number_of_enemies)
        self.game.set_enemy_manager(enemy_manager)
        return enemy_manager

    def reset_player_status(self, player: Player):
        """プレイヤーのステータスを初期状態にリセット"""
        # new_player()から新しいプレイヤーを生成して初期状態を取得
        initial_player = self.new_player()
        
        # 既存のプレイヤーのステータスと装備を初期状態で上書き
        player.status = initial_player.status
        player.inventory = initial_player.inventory  # インベントリごと置き換え
        player.equipped_weapon = initial_player.equipped_weapon
        player.equipped_armor = initial_player.equipped_armor
        player.equipped_left_ring = initial_player.equipped_left_ring
        player.equipped_right_ring = initial_player.equipped_right_ring
        player.turn = 0
        player.is_player = True
