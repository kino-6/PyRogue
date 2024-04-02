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

    def setup_player(self):
        yaml_file = self.assets_manager.get_chara_path("player.yaml")
        with open(yaml_file, "r") as file:
            status_data = yaml.safe_load(file)
        player_status = Status(status_data)
        player = Player(0, 0, player_status, self.logger)
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
