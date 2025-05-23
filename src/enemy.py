import constants as const
from character import Character
from game import Game
from status import Status
from assets_manager import AssetsManager
import os
import yaml
import glob
import math
import random
from collections import deque


class Enemy(Character):
    def __init__(self, x, y, status: Status):
        super().__init__(x, y, status)
        self.behavior = RandomWalkBehavior()
        self.attack_range = 1
        # yamlからchase_powerを取得（なければデフォルト0）
        self.chase_power = getattr(status, "chase_power", 0)
        self.chase_turns = 0

    def update(self, game: Game):
        player = game.get_player()
        if not player:
            return None

        # プレイヤーが睡眠状態の場合は、敵の行動不能状態に関係なく攻撃可能
        if not player.can_act:
            # プレイヤーが見えるかどうかに関係なく攻撃を試みる
            self.behavior = ChasePlayerBehavior()
            action = self.behavior.determine_action(self, game)
            if action:
                return action
            # 攻撃できない場合は、プレイヤーに向かって移動を試みる
            return self.behavior.determine_action(self, game)

        # 通常の行動処理
        if not self.can_act:
            return None

        if self.can_see_player(game):
            self.behavior = ChasePlayerBehavior()
            # 追跡ターンをchase_powerベースでリセット
            self.chase_turns = self.chase_power + random.randint(0, 2)
        elif self.chase_turns > 0:
            self.behavior = ChasePlayerBehavior()
            self.chase_turns -= 1
        else:
            self.behavior = RandomWalkBehavior()

        action = self.behavior.determine_action(self, game)
        return action

    def attack(self, target, game):
        """攻撃処理"""
        # 攻撃の成功を判定
        did_hit, damage = self._roll_attack(target)
        
        if did_hit:
            is_killed = target.take_damage(damage)
            message = f"{self.status.name} attacks {target.status.name} for {damage} damage."
            game.logger.info(message)
            target.add_logger(message)
            
            if is_killed:
                target.die(game)
        else:
            message = f"{self.status.name} missed {target.status.name}!"
            game.logger.info(message)
            target.add_logger(message)

    def _roll_attack(self, target):
        """攻撃の成功判定とダメージ計算"""
        # 基本ダメージ（筋力の半分）
        base_dmg = self.status.strength // 2
        
        # 命中判定（20面ダイス）
        res = random.randint(1, 20)
        # 基本命中率を75%に設定し、レベルと防御力で調整
        base_hit = 5  # 20面ダイスで75%の確率（5以上）
        level_bonus = self.status.level  # レベルが上がるほど命中率が上がる
        # 防御力の影響を軽減（防御力の半分の影響）
        armor_penalty = target.status.armor // 2
        need = base_hit - level_bonus + armor_penalty
        did_hit = res >= need
        
        if did_hit:
            # ステータスからダイス情報を取得してロール
            roll_result = sum(random.randint(1, self.status.dice_sides) 
                            for _ in range(self.status.dice_count))
            
            # 基本ダメージにレベル補正を加算（レベルが上がるほど補正が大きくなる）
            level_bonus = self.status.level // 2
            base_dmg += level_bonus
            
            # 基本ダメージ計算
            max_damage = int(base_dmg / 2) + roll_result
            
            # ばらつきの追加（基本ダメージの1/8）
            rnd_damage = int(max_damage / 8) + 1
            max_damage += random.randint(-rnd_damage, rnd_damage)
            
            # 防御力による軽減（最小ダメージ1を保証）
            damage = max(1, max_damage - target.status.armor)
            
            return True, damage
        else:
            return False, 0

    def calculate_exp_reward(self):
        """経験値報酬の計算"""
        base_exp = self.status.level * self.status.exp  # 基本経験値
        variance = random.randint(-5, 5)    # ±5の変動
        bonus = 0
        
        # 追跡力の高い敵はより多くの経験値
        chase_bonus = int(self.chase_power * 2)
        
        # ボーナス経験値の計算
        if hasattr(self.status, 'is_boss') and self.status.is_boss:
            bonus = 50  # ボス敵の場合のボーナス
        elif hasattr(self.status, 'is_rare') and self.status.is_rare:
            bonus = 30  # レア敵の場合のボーナス
            
        return max(1, base_exp + variance + bonus + chase_bonus)  # 最低1は保証

    def die(self, game):
        """敵の死亡処理"""
        # 経験値の付与
        exp_gain = self.calculate_exp_reward()
        player = game.get_player()
        if player:
            player.gain_experience(exp_gain)
            self.add_logger(f"Defeated {self.status.name}! Gained {exp_gain} experience!")
        
        # アイテムドロップ処理（オプション）
        self.drop_items(game)
        
        # 敵の削除
        game.remove_entity(self)

    def drop_items(self, game):
        """アイテムドロップ処理"""
        # ここにアイテムドロップのロジックを実装
        pass

    def can_see_player(self, game):
        player = game.get_player()
        if not player or player.is_invisible:  # 透明化状態のプレイヤーは見えない
            return False

        # 敵が現在どのタイプのセルにいるかを判断
        current_room_id = game.game_map.room_info[self.y][self.x]
        player_position = game.get_player_position()
        if player_position is None:
            return False

        player_room_id = game.game_map.room_info[player_position[1]][player_position[0]]

        if current_room_id is not None and player_room_id is not None:
            # 両者とも部屋内
            return player_room_id == current_room_id
        else:
            # 通路や部屋の外の場合、距離3以内なら見える
            dx, dy = player_position[0] - self.x, player_position[1] - self.y
            distance = math.sqrt(dx**2 + dy**2)
            return distance <= 3


class EnemyManager:
    def __init__(self):
        self.enemy_data = self.load_enemy_data_from_directory()

    def load_enemy_data_from_directory(self):
        assets_manager = AssetsManager()
        directorys = assets_manager.get_all_enemy_paths()

        enemy_list = []
        for file_path in directorys:
            with open(file_path, "r", encoding="utf-8") as file:
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
        # まず全ての敵を取得
        enemies = [entity for entities in game.entity_positions.values() 
                  for entity in entities if isinstance(entity, Enemy)]
        
        # 各敵の行動を処理
        for enemy in enemies:
            action = enemy.update(game)  # Enemy の行動を決定
            if action:
                game.apply_enemy_action(enemy, action)  # Game クラスに行動を適用させる


class EnemyBehavior:
    def determine_action(self, enemy: Enemy, game: Game):
        # この基底クラスメソッドはオーバーライドされるべきです
        raise NotImplementedError("This method should be overridden by subclasses")


class ChasePlayerBehavior(EnemyBehavior):
    def determine_action(self, enemy: Enemy, game: Game):
        player = game.get_player()
        if not player or player.is_invisible:  # 透明化状態のプレイヤーは追跡しない
            return None

        player_pos = (player.x, player.y)
        enemy_pos = (enemy.x, enemy.y)

        # プレイヤーとの距離を計算（ユークリッド距離）
        dx = abs(player.x - enemy.x)
        dy = abs(player.y - enemy.y)
        
        # 攻撃範囲内（隣接8マス）にいる場合は攻撃
        if dx <= enemy.attack_range and dy <= enemy.attack_range:
            # プレイヤーが睡眠状態の場合は、より積極的に攻撃する
            if not player.can_act:
                message = f"{enemy.status.name} sees you are asleep and attacks!"
                game.logger.info(message)
                player.add_logger(message)
            return {"type": "attack", "target": player}
            
        # 攻撃範囲外の場合は追跡
        next_step = find_next_step(game.game_map, enemy_pos, player_pos)
        if next_step != enemy_pos:
            new_x, new_y = next_step
            # 移動先に他のキャラクターがいないことを確認
            if not any(isinstance(e, Character) for e in game.get_entities_at_position(new_x, new_y)):
                return {"type": "move", "new_x": new_x, "new_y": new_y}

        return None


class RandomWalkBehavior:
    def determine_action(self, enemy: Enemy, game: Game):
        # 8方向のいずれかにランダムに移動する
        possible_moves = [
            (0, 1),  # 上
            (1, 0),  # 右
            (0, -1),  # 下
            (-1, 0),  # 左
            (-1, -1),  # 左上
            (1, -1),  # 右上
            (-1, 1),  # 左下
            (1, 1),  # 右下
        ]
        
        # 移動可能な方向をランダムにシャッフル
        random.shuffle(possible_moves)
        
        for dx, dy in possible_moves:
            new_x, new_y = enemy.x + dx, enemy.y + dy
            
            # 移動先が移動可能で、他のキャラクターがいないことを確認
            if game.is_walkable(new_x, new_y) and not any(isinstance(e, Character) for e in game.get_entities_at_position(new_x, new_y)):
                return {"type": "move", "new_x": new_x, "new_y": new_y}
        
        return None


def find_next_step(game_map, start, goal):
    width, height = game_map.width, game_map.height
    visited = set()
    queue = deque()
    queue.append((start, []))

    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == goal:
            if path:
                return path[0]  # 最初の一歩を返す
            else:
                return (x, y)  # すでにゴール

        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1), (-1,-1), (1,-1), (-1,1), (1,1)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < width and 0 <= ny < height and
                game_map.is_walkable(nx, ny) and (nx, ny) not in visited):
                visited.add((nx, ny))
                queue.append(((nx, ny), path + [(nx, ny)]))
    return start  # ゴールに到達できない場合はその場に留まる
