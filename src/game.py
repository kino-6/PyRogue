import pygame
import random
from map import GameMap
import utils.constants as const
from stair import Stairs
from gold import Gold
from item import Item
from food import Food
from enum import Enum


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

    def set_drawer(self, drawer):
        self.drawer = drawer

    def set_logger(self, logger, log_messages):
        self.logger = logger
        self.log_messages = log_messages

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

    def is_walkable(self, x, y):
        """指定された座標が移動可能かどうかを判断する"""
        walkable_tiles = self.get_walkable_tiles()
        return (x, y) in walkable_tiles

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
        num_items = const.NUMTHINGS + 255
        for _ in range(num_items):
            # ToDo: randam choice
            food = Food()
            self.teleport_entity(food)
            self.add_entity(food)

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
        self.logger.info(message)
        self.drawer.draw_log_window(self.log_messages)
        pygame.display.flip()

    def handle_food_selection(self, character):
        use_turn = False
        food_items = character.get_inventory_with_key(Food)
        if food_items:
            self.renew_logger_window(f"Choose food, {', '.join(food_items.keys())}")
            self.waiting_for_food_selection = True
        else:
            self.renew_logger_window(f"There is no food.")
            self.waiting_for_food_selection = False

        while self.waiting_for_food_selection:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key in const.a_z_KEY:
                        pressed_key = chr(event.key)
                        selected_food = food_items.get(pressed_key)
                        if selected_food:
                            selected_food.use(character)
                            character.inventory.remove_item(selected_food)
                            self.waiting_for_food_selection = False
                            use_turn = True
                            break
                    else:
                        self.waiting_for_food_selection = False
                        break

        # message
        if use_turn:
            self.renew_logger_window("Yammy.")
        elif self.waiting_for_food_selection:
            self.renew_logger_window("This is not food.")
        else:
            self.renew_logger_window("I knew it. I stopped.")

        return use_turn

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
