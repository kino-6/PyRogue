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
import pickle


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

    drawer = Draw(screen, assets_manager, game_map, game)
    game.set_drawer(drawer)

    input_handler = InputHandler(const.GRID_MOVEMENT_SPEED, game, game_map)
    game.set_input_handler(input_handler)

    initializer = GameInitializer(game, logger)
    player = initializer.setup_player()
    stair = initializer.setup_stairs()
    enemy_manager = initializer.setup_enemies(player.status.level, 5)

    game.place_gold_in_dungeon(player.status.level)
    game.place_items_in_dungeon(player.status.level)

    print("Game側 game_map id:", id(game_map))
    print("Draw側 game_map id:", id(drawer.game_map))

    return game, drawer, input_handler, player, enemy_manager


def update_game(game, input_handler, player, enemy_manager, drawer):
    use_turn = False
    input_handler.handle_keys([player.x, player.y])

    action, x, y = input_handler.action
    # print(f"{action=}")

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
        game.spawn_enemy_search_ring_at_player()
        game.explore_around_stairs()
        return False

    def do_console_mode():
        drawer.draw_item_list_window()
        return False

    def do_drop_item():
        return game.handle_drop_item(game.get_player())

    def do_save_game():
        game.save_game()
        return False

    def do_load_game():
        global game, player
        loaded = Game.load_game()
        if loaded is not None:
            game = loaded
            # 参照の再セット
            game.set_drawer(drawer)
            game.set_input_handler(input_handler)
            game.set_enemy_manager(enemy_manager)
            game.set_logger(logger, log_messages)
            player = game.get_player()
            game.renew_logger_window("Game loaded.")
        else:
            game.renew_logger_window("Fail load.")
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
        "console_mode": do_console_mode,
        "drop_item": do_drop_item,
        "save_game": do_save_game,
        "load_game": do_load_game,
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
    # 描画前
    game.unmark_enemy_positions_explored()
    game.mark_enemy_positions_explored()
    drawer.draw_game_map()
    drawer.draw_entity(list(game.entity_positions.values()))
    drawer.draw_log_window(log_messages)
    drawer.draw_status_window(player.status)
    drawer.draw_inventory_window(player)

    pygame.display.flip()

    # 描画後（またはターン終了時）
    # game.unmark_enemy_positions_explored()


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


def save_all(filename="saveall.pkl"):
    globals_dict = {
        "game": game,
        "player": player,
        "enemy_manager": enemy_manager,
        "input_handler": input_handler,
        "drawer": drawer,
        "logger": logger,
        "log_messages": log_messages,
        # 必要なものをすべて
    }
    with open(filename, "wb") as f:
        pickle.dump(globals_dict, f)
    print("全体をセーブしました")


def load_all(filename="saveall.pkl"):
    global game, player, enemy_manager, input_handler, drawer, logger, log_messages
    with open(filename, "rb") as f:
        globals_dict = pickle.load(f)
    game = globals_dict["game"]
    player = globals_dict["player"]
    enemy_manager = globals_dict["enemy_manager"]
    input_handler = globals_dict["input_handler"]
    drawer = globals_dict["drawer"]
    logger = globals_dict["logger"]
    log_messages = globals_dict["log_messages"]
    # 必要なら再セット
    game.set_drawer(drawer)
    game.set_input_handler(input_handler)
    game.set_enemy_manager(enemy_manager)
    game.set_logger(logger, log_messages)
    print("全体をロードしました")


if __name__ == "__main__":
    main()
