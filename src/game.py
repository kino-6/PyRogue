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
import pickle
import yaml
import os


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
        self.console_mode = False
        self.console_input = ""

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

    def update_entity_position(self, entity, old_pos=None):
        """エンティティの位置を更新"""
        if old_pos:
            old_x, old_y = old_pos
            # 古い位置からエンティティを削除
            if (old_x, old_y) in self.entity_positions:
                self.entity_positions[(old_x, old_y)].remove(entity)
                # リストが空になったら辞書からキーを削除
                if not self.entity_positions[(old_x, old_y)]:
                    del self.entity_positions[(old_x, old_y)]
        
        # 新しい位置にエンティティを追加
        new_pos = (entity.x, entity.y)
        if new_pos not in self.entity_positions:
            self.entity_positions[new_pos] = []
        if entity not in self.entity_positions[new_pos]:
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
            old_pos = (enemy.x, enemy.y)
            enemy.x = action["new_x"]
            enemy.y = action["new_y"]
            self.update_entity_position(enemy, old_pos)
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
        """Return player.x, player.y"""
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

    def is_walkable(self, x, y, ignore_characters=False) -> bool:
        """指定された座標が移動可能かどうかを判断する"""
        # タイル自体が移動可能かどうかをチェック
        walkable_tiles = self.get_walkable_tiles()
        if (x, y) not in walkable_tiles:
            return False

        if not ignore_characters:
            # 指定座標にあるエンティティのリストを取得
            entities_at_new_pos = self.entity_positions.get((x, y), [])
            # キャラクターがいる場合のみ移動不可（アイテムは移動可能）
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

    def remove_player(self):
        # entity listからプレーヤーを削除
        from player import Player
        for pos, entities in list(self.entity_positions.items()):
            for entity in list(entities):
                if isinstance(entity, Player):
                    print(f"remove player: {entity.x}, {entity.y}")
                    self.remove_entity(entity)

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
        self.renew_logger_window("all item identified")

    def update_turn(self):
        self.respawn_enemy()

    def mark_initial_visibility(self):
        """プレイヤーの初期位置周辺を探索済みにする"""
        player = self.get_player()
        if player:
            # プレイヤーの周囲を探索済みにする
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    nx, ny = player.x + dx, player.y + dy
                    if 0 <= nx < self.game_map.width and 0 <= ny < self.game_map.height:
                        self.game_map.explored[ny][nx] = True
            
            # プレイヤーがいる部屋全体を探索済みにする
            self.check_new_room_entry(player.x, player.y)

    def enter_new_dungeon(self, enemy_manager):
        """新しいダンジョンへ移動する"""
        # プレイヤーを退避（既存のプレイヤーを使用）
        player = self.get_player()
        
        # エンティティの位置情報を初期化
        self.entity_positions = {}
        
        # 新しいダンジョンを生成
        self.game_map.init_explored()
        
        # プレイヤーを新しい位置に配置して追加
        self.teleport_entity(player)
        self.add_entity(player)
        player.status.level += 1
        
        # 他のエンティティを生成
        enemy_manager.create_enemies(self, player.status.level, const.INITIAL_SPAWN_ENEMY_NUM)
        
        # 階段、アイテム、ゴールドを配置
        stair = Stairs()
        self.teleport_entity(stair)
        self.add_entity(stair)
        self.place_gold_in_dungeon(player.status.level)
        self.place_items_in_dungeon(player.status.level)
        
        # プレイヤーの初期位置周辺を探索済みにする
        self.mark_initial_visibility()

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
            self.renew_logger_window("Generated enemy_search ring at the foot.")
        else:
            self.renew_logger_window("Failed to generate enemy_search ring.")

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
            # 足元にすでにアイテムがあるかチェック
            entities_at_feet = self.get_entities_at_position(character.x, character.y)
            if any(isinstance(e, Item) for e in entities_at_feet):
                self.renew_logger_window("There is already an item at your feet. Cannot be placed.")
                return False
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

    def get_save_data(self):
        player = self.get_player()
        # プレイヤーのインベントリや装備もdict化
        player_data = {
            "x": player.x,
            "y": player.y,
            "status": player.status.__dict__,  # Statusがシンプルな属性のみならOK
            "inventory": [item.__dict__ for item in player.inventory.items],
            "equipped_weapon": player.equipped_weapon.__dict__ if player.equipped_weapon else None,
            "equipped_armor": player.equipped_armor.__dict__ if player.equipped_armor else None,
            "equipped_left_ring": player.equipped_left_ring.__dict__ if player.equipped_left_ring else None,
            "equipped_right_ring": player.equipped_right_ring.__dict__ if player.equipped_right_ring else None,
            "turn": player.turn,
            # 必要に応じて他の属性も
        }

        # マップ情報
        map_data = {
            "tiles": self.game_map.tiles,
            "explored": self.game_map.explored,
            "room_info": self.game_map.room_info,
            # 必要に応じて他のマップ属性も
        }

        # エンティティ情報
        entities_data = []
        for pos, entities in self.entity_positions.items():
            for entity in entities:
                entities_data.append({
                    "class": entity.__class__.__name__,
                    "x": entity.x,
                    "y": entity.y,
                    "data": entity.__dict__,  # 必要に応じてフィルタ
                })

        save_data = {
            "player": player_data,
            "game_map": map_data,
            "entities": entities_data,
            "player_position": self.player_position,
            "explored_rooms": list(self.explored_rooms),
            "level": getattr(player.status, "level", 1),
            "turn": getattr(player, "turn", 0),
            "log_messages": self.log_messages,
            "state": self.state.name if hasattr(self.state, "name") else self.state,
            # 必要に応じて他の属性も
        }
        return save_data

    def set_save_data(self, data):
        map_data = data["game_map"]
        game_map = GameMap()
        game_map.tiles = map_data["tiles"]
        game_map.room_info = map_data["room_info"]

        # exploredの型・サイズを保証
        loaded_explored = map_data["explored"]
        if (len(loaded_explored) == game_map.height and
            all(len(row) == game_map.width for row in loaded_explored)):
            game_map.explored = loaded_explored
        else:
            # サイズが合わない場合は初期化し直す
            game_map.explored = [[False for _ in range(game_map.width)] for _ in range(game_map.height)]
            # 必要なら部分的に復元

        self.game_map = game_map
        self.player_position = data.get("player_position", self.player_position)
        self.entity_positions = data.get("entity_positions", self.entity_positions)
        self.explored_rooms = set(data.get("explored_rooms", []))

        print(len(game_map.explored), len(game_map.explored[0]))
        print(game_map.width, game_map.height)

    def save_game(self, filename="savegame.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self, f)
        self.renew_logger_window("ゲームをセーブしました (F1)。")

    @staticmethod
    def load_game(filename="savegame.pkl"):
        with open(filename, "rb") as f:
            game = pickle.load(f)
        return game

    def __getstate__(self):
        state = self.__dict__.copy()
        # pickleできない属性を除外
        for key in ["drawer", "logger", "input_handler", "enemy_manager"]:
            if key in state:
                del state[key]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        # 除外した属性はロード後に再セット（main.pyで）

    def explore_around_stairs(self):
        from stair import Stairs
        # 全エンティティから階段を探す
        for pos, entities in self.entity_positions.items():
            for entity in entities:
                if isinstance(entity, Stairs):
                    x, y = entity.x, entity.y
                    # 階段の周囲1マスを探索済みに
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.game_map.width and 0 <= ny < self.game_map.height:
                                self.game_map.explored[ny][nx] = True
                    return  # 複数階段があっても最初の1つだけでOK

    def get_entity_at(self, x, y):
        # その座標にいるエンティティを返す
        return [e for e in self.entity_positions.get((x, y), []) if e.x == x and e.y == y]

    def handle_console_event(self, event, player):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.handle_console_command(self.console_input, player)
                self.console_input = ""
                self.console_mode = False
            elif event.key == pygame.K_ESCAPE:
                self.console_input = ""
                self.console_mode = False
            elif event.key == pygame.K_BACKSPACE:
                self.console_input = self.console_input[:-1]
            else:
                if event.unicode.isprintable():
                    self.console_input += event.unicode

    def handle_console_command(self, command, player):
        tokens = command.strip().split()
        if not tokens:
            return
        if tokens[0] == "add_item" and len(tokens) > 1:
            from item_manager import ItemManager
            item_id = tokens[1]
            item = ItemManager().create_item_by_id(item_id)
            if item:
                player.inventory.append(item)
                self.renew_logger_window(f"{item.name} をインベントリに追加しました")
            else:
                self.renew_logger_window("そのIDのアイテムは存在しません")
        elif tokens[0] == "list_items":
            from item_manager import ItemManager
            ids = ItemManager().get_all_item_ids()
            self.renew_logger_window("利用可能なアイテムID: " + ", ".join(ids))
        # 必要に応じて他のコマンドも追加

    def draw_console_input(self, screen):
        font = pygame.font.SysFont(None, 24)
        input_surface = font.render(":" + self.console_input, True, (255, 255, 255), (0, 0, 0))
        screen.blit(input_surface, (10, const.WINDOW_SIZE_H - 30))

    def restart_game(self, old_player):
        """ゲームオーバー時にレベル1から再開する"""
        # プレイヤーを除くすべてのエンティティを削除
        self.entity_positions = {}
        
        # 新しいマップを生成
        self.game_map.init_explored()

        # プレイヤーの状態を初期化
        from game_initializer import GameInitializer
        initializer = GameInitializer(self, self.logger)
        initializer.reset_player_status(old_player)  # 新しいメソッド

        # プレイヤーを新しい位置に配置
        self.teleport_entity(old_player)
        self.add_entity(old_player)

        old_player.status.level = 0
        self.enter_new_dungeon(self.enemy_manager)

        self.identify_all_items()

        # ログメッセージをクリア
        self.log_messages.clear()
        self.renew_logger_window("Welcome back, brave adventurer!")

    def attack_entity(self, attacker, target):
        """エンティティ間の攻撃処理を行う"""
        if hasattr(attacker, 'attack'):
            attacker.attack(target, self)
