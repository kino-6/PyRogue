import pygame
import sys
from player import Player
from input_handler import InputHandler
import utils.constants as const
from map import GameMap
from draw import Draw
from game import Game
from enemy import EnemyManager
from enemy import Enemy
from utils.assets_manager import AssetsManager
from status import Status
from fight import Fight
from stair import Stairs
from food import Food
import random
import logging
import yaml
import threading
import time

# TODO
random.seed(42)

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ログメッセージを保持するリスト
log_messages = []


# ログメッセージをリストに追加するためのハンドラ
class ListHandler(logging.Handler):
    def emit(self, record):
        log_messages.append(self.format(record))


# ハンドラとフォーマットの設定
handler = ListHandler()
formatter = logging.Formatter("%(asctime)s - %(message)s")
# formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def initialize_game():
    pygame.init()
    pygame.key.set_repeat(0)
    screen = pygame.display.set_mode((const.WINDOW_SIZE_W, const.WINDOW_SIZE_H))
    pygame.display.set_caption("PyRogue")
    clock = pygame.time.Clock()
    return screen, clock


def setup_game(screen):
    game_map = GameMap()
    assets_manager = AssetsManager()

    # set game manager
    game = Game(game_map)

    # set logger
    game.set_logger(logger, log_messages)

    # set drawer
    drawer = Draw(screen, assets_manager, game_map)
    game.set_drawer(drawer)

    # set input
    input_handler = InputHandler(const.GRID_MOVEMENT_SPEED, game, game_map)

    # set player
    yaml_file = assets_manager.get_chara_path(const.PLAYER_STATUS)
    with open(yaml_file, "r") as file:
        status_data = yaml.safe_load(file)
    player_status = Status(status_data)

    player = Player(0, 0, player_status, logger)
    game.teleport_entity(player)
    game.add_entity(player)

    # set stair
    stair = Stairs()
    game.teleport_entity(stair)
    game.add_entity(stair)

    # set enemy
    enemy_manager = EnemyManager()
    enemy_manager.create_enemies(game, player.status.level, 5)
    game.set_enemy_manager(enemy_manager)

    # set gold
    game.place_gold_in_dungeon(player.status.level)

    # set items
    game.place_items_in_dungeon(player.status.level)

    return game, drawer, input_handler, player, enemy_manager


def update_game(game, input_handler, player, enemy_manager, drawer):
    # 入力処理
    use_turn = False
    input_handler.handle_keys([player.x, player.y])

    # アクションに基づいてプレイヤーの動作を決定
    action, x, y = input_handler.action
    if action == "move":
        player.move(input_handler.dx, input_handler.dy, game)
        game.update_player_position([player.x, player.y])
        # game.print_entity_positions('Gold')  # debug
        use_turn = True
    elif action == "attack":
        enemies = [
            entity for entities in game.entity_positions.values() for entity in entities if isinstance(entity, Enemy)
        ]
        fight = Fight(player, enemies, game, logger)
        target_entity = next(
            (entity for entity in game.entity_positions.get((x, y), []) if isinstance(entity, Enemy)), None
        )
        if target_entity is not None:
            fight.attack(player, target_entity)
            use_turn = True
    elif action == "descend_stairs":
        if game.player_on_stairs():
            # print("on stair? ", game.player_on_stairs())
            game.enter_new_dungeon(enemy_manager)
    elif action == "rest":
        use_turn = True
    elif action == "eat_food":
        use_turn = game.handle_food_selection(player)
    elif action == "wield_a_weapon":
        use_turn = game.handle_weapon_selection(player)
    elif action == "wear_armor":
        use_turn = game.handle_armor_selection(player)
    else:
        game.update_player_position([player.x, player.y])
        use_turn = False

    game.update_after_player_action()

    # enemy
    if use_turn:
        enemy_manager.update_enemies(game)
        # TODO: add effect rings.
        player.update_turn()
        game.update_turn()


def draw_game(screen, drawer, game, player):
    # draw
    screen.fill((0, 0, 0))
    drawer.draw_game_map()
    drawer.draw_entity(game.entity_positions.values())
    drawer.draw_log_window(log_messages)
    drawer.draw_status_window(player.status)
    drawer.draw_inventory_window(player)

    pygame.display.flip()


def main():
    screen, clock = initialize_game()
    game, drawer, input_handler, player, enemy_manager = setup_game(screen)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        update_game(game, input_handler, player, enemy_manager, drawer)
        draw_game(screen, drawer, game, player)

        pygame.time.delay(const.PYGAME_ONE_TURN_WAIT_MS)
        clock.tick(const.PYGAME_FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
