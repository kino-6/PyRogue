import utils.constants as const
from character import Character
from game import Game
from status import Status
from utils.assets_manager import AssetsManager
import os
import yaml
import glob
import math
import random


class Enemy(Character):
    def __init__(self, x, y, status: Status):
        super().__init__(x, y, status)
        self.behavior = RandomWalkBehavior()
        self.attack_range = 1

    def update(self, game: Game):
        if self.can_see_player(game):
            self.behavior = ChasePlayerBehavior()
        else:
            self.behavior = RandomWalkBehavior()

        action = self.behavior.determine_action(self, game)
        # print(f" ******** {action} ***************")
        if action:
            if action["type"] == "move":
                # 移動アクションを適用
                game.update_entity_position(self, action["new_x"], action["new_y"])
            elif action["type"] == "attack":
                # 攻撃アクションを適用
                self.attack(action["target"])

    def attack(self, target):
        # 攻撃ロジックを実装
        damage = self.status.attack_power
        target.status.current_hp -= damage

    def can_see_player(self, game):
        # 敵が現在どのタイプのセルにいるかを判断
        current_room_id = game.game_map.room_info[self.y][self.x]

        # entity_positionsからプレイヤーの位置を取得
        player_position = game.get_player_position()
        if player_position is None:
            return False

        if current_room_id is not None:
            # 敵が部屋にいる場合、部屋内全体が視界になる
            player_room_id = game.game_map.room_info[player_position[1]][player_position[0]]
            return player_room_id == current_room_id
        else:
            # 敵が通路にいる場合、視界を広げる
            dx, dy = player_position[0] - self.x, player_position[1] - self.y
            distance = math.sqrt(dx**2 + dy**2)

            # 敵がドアにいる場合、視界を部屋内に拡張する
            if game.game_map.get_tile(self.x, self.y) == "+":
                return distance <= 2
            else:
                return distance <= 1


class EnemyManager:
    def __init__(self):
        self.enemy_data = self.load_enemy_data_from_directory()

    def load_enemy_data_from_directory(self):
        assets_manager = AssetsManager()
        directorys = assets_manager.get_all_enemy_paths()

        enemy_list = []
        for file_path in directorys:
            with open(file_path, "r") as file:
                enemy_data = yaml.safe_load(file)
                enemy_list.append(enemy_data)
        return enemy_list

    def tune_enemy_status(self, enemy_status: Status, current_level):
        # ステータスの補正を適用
        lev_add = max(current_level - const.AMULETLEVEL, 0)
        enemy_status.level += lev_add
        enemy_status.max_hp += random.randint(1, 8) * lev_add  # 8面ダイスを lev_add 回振る
        enemy_status.attack_power += lev_add
        enemy_status.defense_power -= lev_add
        enemy_status.exp += lev_add * 10  # 経験値の補正

    def create_enemy(self, current_level, x, y):
        # 現在のレベル以下のモンスターを選択
        suitable_enemies = [e for e in self.enemy_data if e.get("level", 99) <= current_level]
        if not suitable_enemies:
            return None  # 適切なモンスターがいない場合

        # 現在のレベル以下の敵からランダムに選出
        selected_enemy = random.choice(suitable_enemies)

        enemy_status = Status(selected_enemy)
        self.tune_enemy_status(enemy_status, current_level)

        return Enemy(x, y, enemy_status)

    def add_enemy(self, game: Game, current_level):
        """add 1 enemy"""
        enemy = self.create_enemy(current_level, 0, 0)
        if enemy:
            game.teleport_entity(enemy)
            game.add_entity(enemy)

    def create_enemies(self, game: Game, current_level, number_of_enemies=5):
        for _ in range(number_of_enemies):
            self.add_enemy(game, current_level)

    def update_enemies(self, game: Game):
        for entities in list(game.entity_positions.values()):
            for entity in list(entities):
                if isinstance(entity, Enemy):
                    action = entity.update(game)  # Enemy の行動を決定
                    if action:
                        game.apply_enemy_action(entity, action)  # Game クラスに行動を適用させる


class EnemyBehavior:
    def determine_action(self, enemy: Enemy, game: Game):
        # この基底クラスメソッドはオーバーライドされるべきです
        raise NotImplementedError("This method should be overridden by subclasses")


class ChasePlayerBehavior(EnemyBehavior):
    def determine_action(self, enemy: Enemy, game: Game):
        # プレイヤーを取得
        player = game.get_player()

        # プレイヤーの位置に向かって移動するロジック
        dx, dy = player.x - enemy.x, player.y - enemy.y
        distance = math.sqrt(dx**2 + dy**2)

        # 敵がプレイヤーに近づく
        if distance > 0:  # プレイヤーと敵が同じ位置にいないことを確認
            dx, dy = round(dx / distance), round(dy / distance)
            new_x, new_y = int(enemy.x + dx), int(enemy.y + dy)  # 新しい位置を計算

            # 新しい位置が移動可能であることを確認
            if game.is_walkable(new_x, new_y) and new_x != player.x and new_y != player.y:
                return {"type": "move", "new_x": new_x, "new_y": new_y}

        # プレイヤーが一定範囲内にいる場合に攻撃
        if distance <= enemy.attack_range:
            return {"type": "attack", "target": player}

        return None


class RandomWalkBehavior:
    def determine_action(self, enemy: Enemy, game: Game):
        # 8方向のいずれかにランダムに移動する
        dx, dy = random.choice(
            [
                (0, 1),  # 上
                (1, 0),  # 右
                (0, -1),  # 下
                (-1, 0),  # 左
                (-1, -1),  # 左上
                (1, -1),  # 右上
                (-1, 1),  # 左下
                (1, 1),  # 右下
            ]
        )
        new_x, new_y = enemy.x + dx, enemy.y + dy

        if game.is_walkable(new_x, new_y):
            return {"type": "move", "new_x": new_x, "new_y": new_y}
        return None
