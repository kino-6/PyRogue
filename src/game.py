import pygame
import random
from map import GameMap
import constants as const
from stair import Stairs
from gold import Gold
from item import Item
from food import Food
from enum import Enum
from character import Character
from weapon import Weapon, WeaponManager
from armor import Armor, ArmorManager
from ring import Ring, RingManager


class GameState(Enum):
    NORMAL = 1
    FOOD_SELECTION = 2


class Game:
    def __init__(self, game_map: GameMap, start_pos=[0, 0]):
        self.game_map = game_map
        self.state = GameState.NORMAL
        self.reset_player_and_rooms(start_pos)
        self.waiting_for_food_selection = False
        self.entity_positions = {}  # キーは座標タプル (x, y)、値はエンティティ
        self.in_selection_mode = False
        self.temp_enemy_explored = set()  # 一時的に探索済みにしたマス

    def set_drawer(self, drawer):
        self.drawer = drawer

    def set_logger(self, logger, log_messages):
        self.logger = logger
        self.log_messages = log_messages

    def set_input_handler(self, input_handler):
        self.input_handler = input_handler

    def set_enemy_manager(self, enemy_manager):
        self.enemy_manager = enemy_manager

    def reset_player_and_rooms(self, start_pos=[0, 0]):
        # プレイヤーの位置と探索済みの部屋をリセット
        self.player_position = start_pos
        self.explored_rooms = set()
        self.update_player_position(start_pos)

    def update_player_position(self, pos):
        # プレイヤーの位置を更新
        self.player_position = pos

        new_x = pos[0]
        new_y = pos[1]
        self.check_new_room_entry(new_x, new_y)
        self.game_map.mark_adjacent_explored(new_x, new_y)

    def get_entities_at_position(self, x, y):
        return self.entity_positions.get((x, y), [])

    def update_after_player_action(self):
        player = self.get_player()
        for entity in self.get_entities_at_position(player.x, player.y):
            if isinstance(entity, Gold):
                self.player_collect_gold(player, entity)
                break  # ゴールドを1つだけ拾う

    def update_entity_position(self, entity, new_x, new_y):
        # エンティティの位置を更新
        old_pos = (entity.x, entity.y)
        if old_pos in self.entity_positions:
            self.entity_positions[old_pos].remove(entity)
            if not self.entity_positions[old_pos]:
                del self.entity_positions[old_pos]
        entity.x, entity.y = new_x, new_y
        new_pos = (new_x, new_y)
        if new_pos not in self.entity_positions:
            self.entity_positions[new_pos] = []
        self.entity_positions[new_pos].append(entity)

    def add_entity(self, entity):
        pos = (entity.x, entity.y)
        if pos not in self.entity_positions:
            self.entity_positions[pos] = []
        self.entity_positions[pos].append(entity)

    def remove_entity(self, entity):
        pos = (entity.x, entity.y)
        if pos in self.entity_positions and entity in self.entity_positions[pos]:
            self.entity_positions[pos].remove(entity)
            if not self.entity_positions[pos]:
                del self.entity_positions[pos]

    def apply_enemy_action(self, enemy, action):
        # actionに基づいてエンティティの位置を更新する
        if action["type"] == "move":
            self.update_entity_position(enemy, action["new_x"], action["new_y"])
        elif action["type"] == "attack":
            self.attack_entity(enemy, action["target"])

    def check_new_room_entry(self, x, y):
        room_id = self.game_map.room_info[y][x]
        if room_id is not None and room_id not in self.explored_rooms:
            self.explored_rooms.add(room_id)
            self.game_map.mark_room_explored_by_id(room_id)

    def teleport_entity(self, entity):
        """teleport 1 entity"""
        walkable_tiles = self.game_map.get_walkable_tiles()
        if walkable_tiles:
            x, y = random.choice(walkable_tiles)
            entity.x = x
            entity.y = y

    def teleport_all_entities(self):
        for pos, entities in self.entity_positions.items():
            for entity in entities:
                self.teleport_entity(entity)

    def get_player(self):
        # entity_positionsからプレイヤーを取得
        return next(
            (
                entity
                for entities in self.entity_positions.values()
                for entity in entities
                if entity.__class__.__name__ == "Player"
            ),
            None,
        )

    def get_player_position(self):
        # entity_positionsからプレイヤーの位置を取得
        player = next(
            (
                entity
                for entities in self.entity_positions.values()
                for entity in entities
                if entity.__class__.__name__ == "Player"
            ),
            None,
        )
        if player is None:
            return None
        return player.x, player.y

    def get_walkable_tiles(self):
        """移動可能なタイルの座標のリストを返す"""
        walkable_tiles = []
        for y in range(self.game_map.height):
            for x in range(self.game_map.width):
                if self.game_map.is_walkable(x, y):
                    walkable_tiles.append((x, y))
        return walkable_tiles

    def is_walkable(self, x, y) -> bool:
        """指定された座標が移動可能かどうかを判断する"""
        # タイル自体が移動可能かどうかをチェック
        walkable_tiles = self.get_walkable_tiles()
        if (x, y) not in walkable_tiles:
            return False

        # 指定座標にあるエンティティのリストを取得
        entities_at_new_pos = self.entity_positions.get((x, y), [])
        if any(isinstance(entity, Character) for entity in entities_at_new_pos):
            return False

        return True

    def player_collect_gold(self, player, gold_entity):
        player.status.gold += gold_entity.amount
        self.remove_entity(gold_entity)

    def determine_gold_piles(self):
        return random.randint(1, const.MAX_GOLDS)

    def place_gold_in_dungeon(self, current_level):
        num_gold_piles = self.determine_gold_piles()
        for _ in range(num_gold_piles):
            gold = Gold()
            gold.determine_gold_amount(current_level)
            # ゲームマップにゴールドを追加
            self.teleport_entity(gold)
            self.add_entity(gold)

    def place_items_in_dungeon(self, current_level):
        num_items = const.NUMTHINGS + 99  # 99 is debug
        for _ in range(num_items):
            entity_type_list = [Food, Weapon, Armor, Ring]
            entity_type = random.choice(entity_type_list)

            if entity_type == Weapon:
                wm = WeaponManager()
                entity = wm.get_random_weapon()
            elif entity_type == Armor:
                am = ArmorManager()
                entity = am.get_random_armor()
            elif entity_type == Ring:
                ring = RingManager()
                entity = ring.get_random_ring()
            else:
                entity = Food()

            # print(type(entity), entity_type)
            self.teleport_entity(entity)
            self.add_entity(entity)

    def print_entity_positions(self, entity_name):
        for pos, entities in self.entity_positions.items():
            for entity in entities:
                if entity.__class__.__name__ == entity_name:
                    print(f"{entity_name} instance at position: {pos}")

    def player_on_stairs(self):
        """プレイヤーが階段にいるかどうかを判断する"""
        player = self.get_player()
        entities_at_player_pos = self.entity_positions.get((player.x, player.y), [])
        return any(isinstance(entity, Stairs) for entity in entities_at_player_pos)

    def remove_stairs(self):
        # 既存の階段を探して削除する
        for pos, entities in list(self.entity_positions.items()):
            for entity in list(entities):
                if isinstance(entity, Stairs):
                    self.remove_entity(entity)

    def get_item_at_position(self, x, y):
        item = None
        entities = self.get_entities_at_position(x, y)

        for entity in list(entities):
            if isinstance(entity, Item):
                item = entity
                break

        return item

    def remove_item_at_position(self, x, y):
        entities = self.get_entities_at_position(x, y)

        for entity in list(entities):
            if isinstance(entity, Item):
                self.remove_entity(entity)

    def renew_logger_window(self, message):
        # messageが複数行なら分割してリストに追加
        if isinstance(message, str):
            lines = message.splitlines()
        else:
            lines = list(message)
        self.log_messages.extend(lines)
        self.drawer.draw_log_window(self.log_messages)
        pygame.display.flip()

    def handle_food_selection(self, character):
        food_items = character.get_inventory_with_key(Food)
        if not food_items:
            self.renew_logger_window("There is no food.")
            return False

        self.renew_logger_window(f"Choose food, {', '.join(food_items.keys())}")

        selected_food = self.wait_for_item_selection(food_items)
        if selected_food:
            selected_food.use(character)
            character.inventory.remove_item(selected_food)
            self.renew_logger_window("Yammy.")
            return True
        else:
            self.renew_logger_window("This is not food.")
            return False

    def handle_weapon_selection(self, character):
        weapon_items = character.get_inventory_with_key(Weapon)
        if not weapon_items:
            self.renew_logger_window("There is no weapon.")
            return False

        self.renew_logger_window(f"Choose weapon, {', '.join(weapon_items.keys())}")

        selected_weapon = self.wait_for_item_selection(weapon_items)
        if selected_weapon:
            # print(character.equipped_weapon)
            if character.equipped_weapon:
                character.equipped_weapon.unequip(character)
            selected_weapon.equip(character)
            self.renew_logger_window(f"You are now wielding {selected_weapon.display_name}")
            return True
        else:
            self.renew_logger_window("This is not weapon.")
            return False

    def handle_armor_selection(self, character):
        armor_items = character.get_inventory_with_key(Armor)
        if not armor_items:
            self.renew_logger_window("There is no armor.")
            return False

        self.renew_logger_window(f"Choose armor, {', '.join(armor_items.keys())}")

        selected_armor = self.wait_for_item_selection(armor_items)
        if selected_armor:
            if character.equipped_armor:
                character.equipped_armor.unequip(character)
            selected_armor.equip(character)
            self.renew_logger_window(f"You are now wearing {selected_armor.display_name}")
            return True
        else:
            self.renew_logger_window("This is not armor.")
            return False

    def handle_ring_selection(self, character):
        ring_items = character.get_inventory_with_key(Ring)
        if not ring_items:
            self.renew_logger_window("There is no ring.")
            return False

        self.renew_logger_window(f"Choose a ring, {', '.join(ring_items.keys())}")

        selected_ring = self.wait_for_item_selection(ring_items)
        if selected_ring:
            character.equip(Ring, selected_ring, "left")
            self.renew_logger_window(f"You are now wearing {selected_ring.display_name} on your left hand.")
            return True
        else:
            self.renew_logger_window("This is not a ring.")
            return False

    def handle_inspect_item(self, character):
        self.in_selection_mode = True
        # インベントリからアイテム選択
        items = character.inventory.items
        if not items:
            self.renew_logger_window("There are no items in your inventory.")
            self.in_selection_mode = False
            return
        self.renew_logger_window("Press the key of the item you wish to check.")
        selected_item = self.wait_for_item_selection({k: v for k, v in zip("abcdefghijklmnopqrstuvwxyz", items)})
        if selected_item:
            info = selected_item.get_info()
            self.renew_logger_window(info)
        else:
            self.renew_logger_window("Item was not selected.")
        self.in_selection_mode = False

    def wait_for_item_selection(self, items):
        selected_key = None
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key in const.a_z_KEY:
                        pressed_key = chr(event.key)
                        selected_key = pressed_key
                        break
                    elif event.key == pygame.K_ESCAPE:
                        return None
            if selected_key:
                # 選択キーが離されるまで待つ
                waiting_release = True
                while waiting_release:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYUP and chr(event.key) == selected_key:
                            waiting_release = False
                    pygame.time.wait(10)
                return items.get(selected_key)
            pygame.time.wait(10)

    def respawn_enemy(self):
        player = self.get_player()

        if player.turn % const.RESPAWN_TURN == 0:
            respawn = random.randint(const.RESPAWN_DICE_MIN, const.RESPAWN_DICE_MAX)
            if respawn == 0:
                self.enemy_manager.create_enemies(self, player.status.level, 1)

    def identify_all_items(self):
        player = self.get_player()
        for item in player.inventory.items:
            # 武器・防具・指輪などに応じて鑑定メソッドを呼ぶ
            if hasattr(item, "appraisal_at_judgment"):
                item.appraisal_at_judgment()
            elif hasattr(item, "appraisal"):
                item.appraisal()
        self.renew_logger_window("all item identified (DebugMode)")

    def update_turn(self):
        self.respawn_enemy()

    def enter_new_dungeon(self, enemy_manager):
        """新しいダンジョンへ移動する"""
        # プレイヤーを退避
        player = self.get_player()
        self.reset_player_and_rooms()

        # 既存の階段を削除
        self.remove_stairs()

        # 新しいダンジョンを生成
        self.game_map.init_explored()

        # エンティティの位置情報を初期化
        self.entity_positions = {}

        # プレイヤーを新しいダンジョンのスタート位置に配置
        self.teleport_entity(player)
        self.add_entity(player)
        player.status.level += 1

        # プレイヤーを除くエンティティを再生成
        enemy_manager.create_enemies(self, player.status.level, 5)

        # 新しい階段を生成して追加
        stair = Stairs()
        self.teleport_entity(stair)
        self.add_entity(stair)

        # new gold
        self.place_gold_in_dungeon(player.status.level)

        # set items
        self.place_items_in_dungeon(player.status.level)

    def draw_help(self):
        keymap = self.input_handler.keymap
        self.drawer.draw_help_window(keymap)
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    waiting = False
            pygame.time.wait(10)

    def spawn_enemy_search_ring_at_player(self):
        from ring import RingManager
        player = self.get_player()
        ring_manager = RingManager()
        ring = ring_manager.get_ring_by_effect("enemy_search")
        if ring:
            ring.x = player.x
            ring.y = player.y
            self.add_entity(ring)
            self.renew_logger_window("足元に enemy_search リングを生成しました。")
        else:
            self.renew_logger_window("enemy_search リングの生成に失敗しました。")

    def mark_enemy_positions_explored(self):
        """enemy_search_active時、敵のいるマスを一時的に探索済みにする"""
        player = self.get_player()
        if not player or not getattr(player, "enemy_search_active", False):
            return
        from enemy import Enemy
        for pos, entities in self.entity_positions.items():
            for entity in entities:
                if entity.__class__.__name__ == "Enemy":
                    x, y = entity.x, entity.y
                    if not self.game_map.explored[y][x]:
                        self.game_map.explored[y][x] = True
                        self.temp_enemy_explored.add((x, y))

    def unmark_enemy_positions_explored(self):
        """一時的に探索済みにしたマスを元に戻す"""
        for x, y in self.temp_enemy_explored:
            self.game_map.explored[y][x] = False
        self.temp_enemy_explored.clear()

    def handle_drop_item(self, character):
        items = character.inventory.items
        if not items:
            self.renew_logger_window("There are no items in your inventory.")
            return False
        self.renew_logger_window("Press the key of the item you wish to discard.")
        selected_item = self.wait_for_item_selection({k: v for k, v in zip("abcdefghijklmnopqrstuvwxyz", items)})
        if selected_item:
            # インベントリから削除
            character.inventory.remove_item(selected_item)
            # 足元に配置
            selected_item.x = character.x
            selected_item.y = character.y
            self.add_entity(selected_item)
            self.renew_logger_window(f"{selected_item.display_name} on the ground.")
            return True
        else:
            self.renew_logger_window("Item was not selected.")
            return False
