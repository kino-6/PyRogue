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
from player import Player
import pickle
import yaml
import os
from potion import Potion, PotionManager
from effect import EFFECT_MAP


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
        self._restart_game = False
        self.console_input = ""
        self.potion_manager = PotionManager()  # PotionManagerを初期化

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
        """エンティティの位置を更新する"""
        new_pos = (entity.x, entity.y)
        
        # 古い位置が指定されている場合、そこからエンティティを削除
        if old_pos:
            old_x, old_y = old_pos
            if (old_x, old_y) in self.entity_positions:
                # エンティティが存在する場合のみ削除を試みる
                if entity in self.entity_positions[(old_x, old_y)]:
                    self.entity_positions[(old_x, old_y)].remove(entity)
                # リストが空になった場合、キーを削除
                if not self.entity_positions[(old_x, old_y)]:
                    del self.entity_positions[(old_x, old_y)]
        
        # 新しい位置にエンティティを追加
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
            new_x, new_y = action["new_x"], action["new_y"]
            
            # 移動先に他のキャラクターがいないことを確認
            entities_at_new_pos = self.get_entities_at_position(new_x, new_y)
            if not any(isinstance(e, Character) for e in entities_at_new_pos):
                enemy.x = new_x
                enemy.y = new_y
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
            # 既に他のキャラクターがいるマスを除外
            available_tiles = [
                (x, y) for x, y in walkable_tiles
                if not any(isinstance(e, Character) for e in self.get_entities_at_position(x, y))
            ]
            if available_tiles:
                x, y = random.choice(available_tiles)
                entity.x = x
                entity.y = y
            else:
                # 利用可能なマスがない場合は、ランダムな位置に配置
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
            entity_type_list = [Food, Weapon, Armor, Ring, Potion]  # ポーションを追加
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
            elif entity_type == Potion:  # ポーションの生成を追加
                pm = PotionManager()
                entity = pm.get_random_potion()
            else:
                entity = Food()

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
            room_id = self.game_map.room_info[player.y][player.x]
            if room_id is not None:
                self.explored_rooms.add(room_id)
                self.game_map.mark_room_explored_by_id(room_id)

    def enter_new_dungeon(self, enemy_manager):
        """新しいダンジョンへ移動する"""
        # プレイヤーを取得
        player = self.get_player()
        if player is None:
            print("Error: No player found in enter_new_dungeon")
            return
        
        # フェードアウト効果
        screen = pygame.display.get_surface()
        dark_surface = pygame.Surface(screen.get_size())
        dark_surface.fill((0, 0, 0))
        
        # 徐々に暗くする
        for alpha in range(0, 255, 5):
            dark_surface.set_alpha(alpha)
            screen.blit(dark_surface, (0, 0))
            pygame.display.flip()
            pygame.time.wait(20)
        
        # 階層情報の表示
        font = pygame.font.Font(None, 48)
        floor_text = font.render(f"Floor {player.status.level} -> {player.status.level + 1}", True, (255, 255, 255))
        text_rect = floor_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        
        # 画面を真っ暗にしてから階層情報を表示
        dark_surface.set_alpha(255)
        screen.blit(dark_surface, (0, 0))
        screen.blit(floor_text, text_rect)
        pygame.display.flip()
        pygame.time.wait(1000)  # 1秒間表示
        
        # エンティティの位置情報を初期化（プレイヤーを除く）
        old_player_pos = None
        if player:
            old_player_pos = (player.x, player.y)
        
        self.entity_positions = {}
        
        # プレイヤーを再配置
        if old_player_pos:
            self.add_entity(player)
        
        # 新しいダンジョンを生成
        self.game_map.init_explored()
        self.explored_rooms.clear()  # 探索済み部屋のリストもクリア
        
        # プレイヤーを新しい位置に配置
        self.teleport_entity(player)
        player.status.level += 1
        
        # 他のエンティティを生成
        enemy_manager.create_enemies(self, player.status.level, const.INITIAL_SPAWN_ENEMY_NUM)
        
        # 階段、アイテム、ゴールドを配置
        stair = Stairs()
        self.teleport_entity(stair)
        self.add_entity(stair)
        self.place_gold_in_dungeon(player.status.level)
        self.place_items_in_dungeon(player.status.level)
        
        # プレイヤーの初期位置周辺と部屋を探索済みにする
        self.mark_initial_visibility()
        
        # フェードイン効果
        for alpha in range(255, 0, -5):
            # ゲーム画面を描画
            self.drawer.draw_game_map()
            self.drawer.draw_entity(self.entity_positions.values())
            self.drawer.draw_status_window(player.status)
            self.drawer.draw_inventory_window(player)
            self.drawer.draw_log_window(self.log_messages)
            
            # 暗い画面を重ねる
            dark_surface.set_alpha(alpha)
            screen.blit(dark_surface, (0, 0))
            pygame.display.flip()
            pygame.time.wait(20)
        
        # ログに階層移動のメッセージを追加
        self.renew_logger_window(f"Descended to Floor {player.status.level}...")

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
            elif event.key == pygame.K_t:  # 投げるコマンドを追加
                self.handle_throw_item(player)
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

    def restart_game(self, old_player: Player):
        """ゲームオーバー時にレベル1から再開する"""
        # プレイヤーの状態を初期化
        from game_initializer import GameInitializer
        initializer = GameInitializer(self, self.logger)
        initializer.reset_player_status(old_player)

        # エンティティの位置情報を初期化
        self.entity_positions = {}
        
        # プレイヤーを新しい位置に配置して追加
        self.teleport_entity(old_player)
        self.add_entity(old_player)

        # レベルを0に設定（enter_new_dungeonで1になる）
        old_player.status.level = 0
        
        # 新しいダンジョンに入る（この中でマップの初期化も行われる）
        self.enter_new_dungeon(self.enemy_manager)
        self.identify_all_items()

        # ログメッセージをクリア
        self.log_messages.clear()
        self.renew_logger_window("Welcome back, brave adventurer!")

        self._restart_game = True

    def attack_entity(self, attacker, target):
        """エンティティ間の攻撃処理を行う"""
        if hasattr(attacker, 'attack'):
            attacker.attack(target, self)

    def handle_potion_selection(self, character):
        potion_items = character.get_inventory_with_key(Potion)
        if not potion_items:
            self.renew_logger_window("There is no potion.")
            return False

        self.renew_logger_window(f"Choose potion, {', '.join(potion_items.keys())}")

        selected_potion = self.wait_for_item_selection(potion_items)
        if selected_potion:
            selected_potion.use(character)
            character.inventory.remove_item(selected_potion)
            # インベントリ内のポーションの表示名を更新
            self.potion_manager.update_inventory_potions(character.inventory.items)
            self.renew_logger_window(f"You drink the {selected_potion.display_name}")
            # インベントリの表示を更新
            self.drawer.draw_inventory_window(character)
            pygame.display.flip()
            return True
        else:
            self.renew_logger_window("This is not potion.")
            return False

    def handle_throw_item(self, character):
        """アイテムを投げる処理"""
        # インベントリから投げるアイテムを選択
        items = character.inventory.items
        if not items:
            self.renew_logger_window("You have nothing to throw.")
            return False

        self.renew_logger_window("Select an item to throw:")
        selected_item = self.wait_for_item_selection({k: v for k, v in zip("abcdefghijklmnopqrstuvwxyz", items)})
        if not selected_item:
            return False

        # 投げる方向を選択
        self.renew_logger_window("Select direction to throw (use arrow keys):")
        direction = self.wait_for_direction()
        if not direction:
            return False

        # 投げる処理を実行
        self.throw_item(character, selected_item, direction)
        return True

    def wait_for_direction(self):
        """方向入力を待つ"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    # 矢印キー
                    if event.key == pygame.K_UP or event.key == pygame.K_KP8:
                        return (0, -1)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_KP2:
                        return (0, 1)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_KP4:
                        return (-1, 0)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_KP6:
                        return (1, 0)
                    # テンキー（斜め方向）
                    elif event.key == pygame.K_KP7:  # 左上
                        return (-1, -1)
                    elif event.key == pygame.K_KP9:  # 右上
                        return (1, -1)
                    elif event.key == pygame.K_KP1:  # 左下
                        return (-1, 1)
                    elif event.key == pygame.K_KP3:  # 右下
                        return (1, 1)
                    elif event.key == pygame.K_ESCAPE:
                        return None
            pygame.time.delay(100)

    def throw_item(self, character, item, direction):
        """アイテムを投げる"""
        if not character.inventory.has_item(item):
            return False

        # 装備品の場合、装備を解除する
        if hasattr(item, 'is_equipped') and item.is_equipped:
            item.unequip(character)

        # インベントリからアイテムを削除
        character.inventory.remove_item(item)

        # 投げる方向に壁があるかチェック
        current_x, current_y = character.x, character.y
        target_x, target_y = current_x + direction[0], current_y + direction[1]

        # 壁に当たるまで投げる
        while True:
            if not self.game_map.is_walkable(target_x, target_y):
                # 壁に当たった場合、その前の位置にアイテムを配置
                drop_x, drop_y = target_x - direction[0], target_y - direction[1]
                
                # その位置にアイテムがあるかチェック
                if not any(isinstance(e, Item) for e in self.get_entities_at_position(drop_x, drop_y)):
                    # アイテムがない場合はその位置に配置
                    item.x, item.y = drop_x, drop_y
                    self.add_entity(item)
                    return True
                else:
                    # アイテムがある場合は周囲16マスの空いているマスを探す
                    for radius in range(1, 5):  # 1から4までの半径で探索
                        for dx in range(-radius, radius + 1):
                            for dy in range(-radius, radius + 1):
                                # 現在の半径の外側のマスのみをチェック
                                if abs(dx) == radius or abs(dy) == radius:
                                    check_x, check_y = drop_x + dx, drop_y + dy
                                    if (self.game_map.is_walkable(check_x, check_y) and 
                                        not any(isinstance(e, Item) for e in self.get_entities_at_position(check_x, check_y))):
                                        item.x, item.y = check_x, check_y
                                        self.add_entity(item)
                                        return True
                    
                    # 空いているマスが見つからない場合はアイテムを消去
                    self.renew_logger_window(f"The {item.display_name} disappears into the void!")
                    return True

            # 敵に当たったかチェック
            for enemy in self.get_entities_at_position(target_x, target_y):
                if isinstance(enemy, Character) and not enemy.is_player:
                    # 敵に当たった場合、ダメージを与える
                    damage = 1  # 基本ダメージ
                    if hasattr(item, 'throw_dice'):
                        damage = self.calculate_throw_damage(item)
                    enemy.take_damage(damage)
                    self.renew_logger_window(f"{character.status.name} threw {item.display_name} at {enemy.status.name} for {damage} damage!")

                    # アイテムにエフェクトがある場合は適用
                    if hasattr(item, 'effect') and item.effect is not None:
                        item.effect.apply_effect(enemy)
                        self.renew_logger_window(f"The {item.display_name}'s effect was applied to {enemy.status.name}!")

                    return True

            # 次の位置に移動
            target_x += direction[0]
            target_y += direction[1]

        return False

    def calculate_throw_damage(self, item):
        """投げたアイテムのダメージを計算"""
        if not hasattr(item, 'throw_dice'):
            return 1  # デフォルトのダメージ

        dice_str = item.throw_dice
        if not dice_str:
            return 1

        # ダイスロールの結果を計算
        total_damage = 0
        for part in dice_str.split('+'):
            if 'd' in part:
                num_dice, num_sides = map(int, part.split('d'))
                total_damage += sum(random.randint(1, num_sides) for _ in range(num_dice))
            else:
                total_damage += int(part)

        return max(1, total_damage)  # 最低1のダメージを保証

    def get_potion_manager(self):
        """PotionManagerのインスタンスを返す"""
        return self.potion_manager
