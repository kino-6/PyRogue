import init_project

import pygame
import sys
from player import Player
from input_handler import InputHandler
import constants as const
from map import GameMap
from draw import Draw
from game import Game
from enemy import EnemyManager
from enemy import Enemy
from assets_manager import AssetsManager
from status import Status
from fight import Fight
from stair import Stairs
from food import Food
import random
import logging
import yaml
import threading
import time
from game_initializer import GameInitializer


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

    game = Game(game_map)
    game.set_logger(logger, log_messages)

    drawer = Draw(screen, assets_manager, game_map)
    game.set_drawer(drawer)

    input_handler = InputHandler(const.GRID_MOVEMENT_SPEED, game, game_map)
    game.set_input_handler(input_handler)

    initializer = GameInitializer(game, logger)
    player = initializer.setup_player()
    stair = initializer.setup_stairs()
    enemy_manager = initializer.setup_enemies(player.status.level, 5)

    game.place_gold_in_dungeon(player.status.level)
    game.place_items_in_dungeon(player.status.level)

    return game, drawer, input_handler, player, enemy_manager


def update_game(game, input_handler, player, enemy_manager, drawer):
    use_turn = False
    input_handler.handle_keys([player.x, player.y])

    action, x, y = input_handler.action
    print(f"{action=}")

    # アクション名→処理関数のディスパッチテーブル
    def do_move():
        player.move(input_handler.dx, input_handler.dy, game)
        game.update_player_position([player.x, player.y])
        return True

    def do_attack():
        enemies = [
            entity for entities in game.entity_positions.values() for entity in entities if isinstance(entity, Enemy)
        ]
        fight = Fight(player, enemies, game, logger)
        target_entity = next(
            (entity for entity in game.entity_positions.get((x, y), []) if isinstance(entity, Enemy)), None
        )
        if target_entity is not None:
            fight.attack(player, target_entity)
            return True
        return False

    def do_descend_stairs():
        if game.player_on_stairs():
            game.enter_new_dungeon(enemy_manager)
        return False

    def do_rest():
        return True

    def do_eat_food():
        return game.handle_food_selection(player)

    def do_wield_a_weapon():
        return game.handle_weapon_selection(player)

    def do_wear_armor():
        return game.handle_armor_selection(player)

    def do_put_on_a_ring():
        return game.handle_ring_selection(player)

    def do_inspect_item():
        game.handle_inspect_item(game.get_player())
        return False

    def do_draw_help():
        game.draw_help()
        return False

    def do_debug_mode():
        game.identify_all_items()
        return False

    def do_none():
        game.update_player_position([player.x, player.y])
        return False

    # アクション名→関数のマッピング
    action_map = {
        "move": do_move,
        "attack": do_attack,
        "descend_stairs": do_descend_stairs,
        "rest": do_rest,
        "eat_food": do_eat_food,
        "wield_a_weapon": do_wield_a_weapon,
        "wear_armor": do_wear_armor,
        "put_on_a_ring": do_put_on_a_ring,
        "inspect_item": do_inspect_item,
        "draw_help": do_draw_help,
        "debug_mode": do_debug_mode,
        "none": do_none,
    }

    # アクション名で分岐
    use_turn = action_map.get(action, do_none)()

    game.update_after_player_action()

    # enemy
    if use_turn:
        enemy_manager.update_enemies(game)
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
