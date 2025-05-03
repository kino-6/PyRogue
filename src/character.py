from status import Status
from entity import Entity
from item import Item
from inventory import Inventory
import constants as const
import string
from typing import Type
from typing import Dict, Optional
from weapon import Weapon
from armor import Armor
from ring import Ring
from effect import RegenerationEffect, StrengthEffect, ProtectionEffect
import pygame
import sys


class Character(Entity):
    def __init__(self, x, y, status: Status, logger=None):
        super().__init__(x, y, status.char, status.color)
        self.status = status
        self.logger = logger
        self.turn = 0
        self.turns_since_last_recovery = 0
        self.inventory = Inventory()
        self.equipped_weapon = None
        self.equipped_armor = None
        self.equipped_right_ring = None
        self.equipped_left_ring = None
        self.enemy_search_active = False
        self.damage_bonus = 0
        self.hit_bonus = 0
        self.effects = []  # エフェクトのリストを保持
        self.is_player = False  # デフォルトはFalse
        self.is_invisible = False  # 透明化状態を追加
        self.evasion_bonus = 0  # 回避率ボーナスを追加

    def get_looped_element(self, idx, looped_list):
        looped_idx = idx % len(looped_list)
        return looped_list[looped_idx]

    def get_inventory_with_key(self, item_type: Type[Item]) -> Dict[str, Optional[Item]]:
        """
        インベントリのキーに対応した特定の型のアイテムのリストを作成するメソッド

        Args:
        item_type (Type[Item]): 取得するアイテムの型

        Returns:
        Dict[str, Optional[Item]]: インベントリのキーに対応したアイテムの辞書
        """
        KEY_LIST = list(string.ascii_lowercase)
        items_by_key = {}

        for key, item in zip(KEY_LIST, self.inventory.items):
            if isinstance(item, item_type):
                items_by_key[key] = item
        return items_by_key

    def get_inventory_str_list(self):
        KEY_LIST = list(string.ascii_lowercase)
        result_str = []
        is_defined_list = []
        for i, item in enumerate(self.inventory.items):
            idx_key = self.get_looped_element(i, KEY_LIST)
            result_str.append(f"{idx_key}) {item.display_name}")
            is_defined_list.append(item.is_defined)
        return result_str, is_defined_list

    def get_char(self):
        return self.status.char

    def move(self, dx, dy, game):
        new_x, new_y = int(self.x + dx), int(self.y + dy)
        if game.game_map.is_walkable(new_x, new_y):
            self.x, self.y = new_x, new_y
            self.pick_up_item_at_feet(game)

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, damage):
        # 現在のHPからダメージを引く
        self.status.current_hp -= damage
        
        # HPが0以下になった場合の処理
        if self.status.current_hp <= 0:
            self.status.current_hp = 0
            self.add_logger(f"{self.status.name} was defeated!")
            return True  # 死亡したことを返す
            
        return False  # 生存していることを返す

    def heal_damage(self, amount):
        # HPを回復し、最大HPを超えないようにする
        self.status.current_hp += amount
        if self.status.current_hp > self.status.max_hp:
            self.status.current_hp = self.status.max_hp

    def update_turn(self):
        self.turn += 1
        self.update_nutrition()
        self.natural_recovery()
        self.update_on_turn()

    def sate_hunger(self, nutrition_change):
        self.status.food_left = max(0, min(self.status.food_left + nutrition_change, const.STOMACHSIZE))

    def update_nutrition(self, nutrition_change=-const.EACH_TURN_STARVE):
        self.sate_hunger(nutrition_change)
        self.check_hunger_state()

    def check_hunger_state(self):
        # 満腹度に応じた状態をチェックするロジックを実装
        pass

    def natural_recovery(self):
        recovery_amount = int(self.status.max_hp / const.RECOVERY_AMOUNT_CONF) + 1
        recovery_interval = const.RECOVERY_INTERVAL
        self.turns_since_last_recovery += 1

        # 一定ターン経過後にHPを回復
        if self.turns_since_last_recovery >= recovery_interval:
            self.heal_damage(recovery_amount)
            self.turns_since_last_recovery = 0  # ターン数をリセット

    def add_logger(self, msg: str):
        if self.logger:
            self.logger.info(msg)

    def pick_up_item_at_feet(self, game):
        item = game.get_item_at_position(self.x, self.y)
        if item:
            if len(self.inventory.items) < const.INVENTORY_MAX:
                self.inventory.add_item(item)
                game.remove_item_at_position(self.x, self.y)
                self.add_logger(f"{self.status.name} pick {item.display_name}")
            else:
                self.add_logger(f"{self.status.name} can't pick up {item.display_name}, my bags full.")

    def calculate_exp_to_next_level(self):
        """次のレベルに必要な経験値を計算"""
        base_exp = const.BASE_EXP
        level_factor = const.LEVEL_FACTOR
        return int(base_exp * (level_factor ** (self.status.exp_level - 1)))

    def gain_experience(self, value):
        """経験値獲得処理"""
        self.status.exp += value
        self.status.next_exp = self.calculate_exp_to_next_level()
        
        # レベルアップチェック
        while self.status.exp >= self.calculate_exp_to_next_level():
            self.level_up()

    def level_up(self, debug=False):
        """レベルアップ処理"""
        import random
        
        # 経験値の処理
        if debug is False:
            self.status.exp -= self.calculate_exp_to_next_level()
        self.status.exp_level += 1

        # ステータス上昇値の計算
        hp_gain = random.randint(1, 5)
        strength_gain = random.randint(1, 2)

        # ステータスの更新
        self.status.max_hp += hp_gain
        self.status.current_hp += hp_gain
        self.status.strength += strength_gain
        # self.status.defense_power += defense_gain

        # ログ出力
        self.add_logger(f"{self.status.name} has been raised to level {self.status.level}!")
        self.add_logger(f"MAX HP +{hp_gain}")
        self.add_logger(f"Str + {strength_gain}")

    def level_down(self):
        """レベルダウン処理"""
        import random

        if self.status.exp_level > 1:  # レベル1未満にはならない
            self.status.exp_level -= 1

            # ステータス減少値の計算
            hp_loss = random.randint(1, 5)
            strength_loss = random.randint(1, 2)  # 1-3の攻撃力減少
            # defense_loss = random.randint(0, 1)  # 0-1の防御力減少

            # ステータスの更新（最低値を下回らないように）
            self.status.max_hp = max(1, self.status.max_hp - hp_loss)
            self.status.current_hp = min(self.status.current_hp, self.status.max_hp)
            self.status.strength_power = max(1, self.status.strength - strength_loss)
            # self.status.defense_power = max(0, self.status.defense_power - defense_loss)

            # 経験値のリセット
            self.status.exp = 0

            # ログ出力
            self.add_logger(f"{self.status.name}is the level down...")
            self.add_logger(f"MAX HP -{hp_loss}")
            self.add_logger(f"Attack -{attack_loss}")

    def get_status_info(self):
        """ステータス情報の取得"""
        info = []
        info.append(f"Name: {self.status.name}")
        info.append(f"Level: {self.status.level}")
        info.append(f"HP: {self.status.current_hp}/{self.status.max_hp}")
        info.append(f"EXP: {self.status.exp}/{self.calculate_exp_to_next_level()}")
        info.append(f"Attack: {self.status.attack_power}")
        info.append(f"Defense: {self.status.defense_power}")
        return info

    def use_item(self, item):
        item.use(self)

    def equip(self, type, equipment, position="left"):
        if type == Weapon:
            self.equipped_weapon = equipment
        elif type == Armor:
            self.equipped_armor = equipment
            if equipment:
                self.status.armor = equipment.armor
        elif type == Ring:
            if position == "left":
                if self.equipped_left_ring:
                    self.equipped_left_ring.unequip(self)
                self.equipped_left_ring = equipment
                equipment.equip(self)

    def update_on_turn(self):
        """キャラクターのターン開始時の処理"""
        # 全てのエフェクトのon_turnを実行
        for effect in self.effects:
            effect.on_turn(self)

    def add_effect(self, effect):
        """エフェクトを追加"""
        self.effects.append(effect)

    def remove_effect(self, effect):
        """エフェクトを除去"""
        if effect in self.effects:
            self.effects.remove(effect)

    def die(self, game):
        """キャラクターが死亡時の処理"""
        if self.is_player:  # プレイヤーの場合
            self.status.current_hp = 0
            self.add_logger("You have been defeated...")
            
            # 最後のゲーム状態を描画
            game.drawer.draw_game_map()
            game.drawer.draw_entity(game.entity_positions.values())
            game.drawer.draw_status_window(self.status)
            game.drawer.draw_inventory_window(self)
            game.drawer.draw_log_window(game.log_messages)
            pygame.display.flip()
            
            # プレイヤーの入力を待つ
            screen = pygame.display.get_surface()
            font = pygame.font.Font(None, 48)  # フォントサイズを大きく
            text = font.render("Press ENTER to continue...", True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            
            # 縁取り用の黒いテキストを8方向にずらして描画
            outline_offset = 2
            for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
                outline_rect = text_rect.copy()
                outline_rect.x += dx * outline_offset
                outline_rect.y += dy * outline_offset
                outline_text = font.render("Press ENTER to continue...", True, (0, 0, 0))
                screen.blit(outline_text, outline_rect)
            
            # 点滅用のカウンター
            blink_counter = 0
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                            waiting = False
                    elif event.type == pygame.QUIT:  # ウィンドウの×ボタン
                        pygame.quit()
                        sys.exit()
                
                # 点滅処理（30フレームごとに表示/非表示を切り替え）
                blink_counter = (blink_counter + 1) % 60
                if blink_counter < 30:
                    # 縁取りを描画
                    for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
                        outline_rect = text_rect.copy()
                        outline_rect.x += dx * outline_offset
                        outline_rect.y += dy * outline_offset
                        outline_text = font.render("Press ENTER to continue...", True, (0, 0, 0))
                        screen.blit(outline_text, outline_rect)
                    # メインテキストを描画
                    screen.blit(text, text_rect)
                pygame.display.flip()
                pygame.time.wait(10)
            
            # 画面を徐々に暗転
            dark_surface = pygame.Surface(screen.get_size())
            dark_surface.fill((0, 0, 0))
            
            # フェードアウト効果
            for alpha in range(0, 255, 5):
                dark_surface.set_alpha(alpha)
                screen.blit(dark_surface, (0, 0))
                pygame.display.flip()
                pygame.time.wait(20)
            
            # RIPと死亡情報の表示
            font = pygame.font.Font(None, 74)
            rip_text = font.render("REST IN PEACE", True, (255, 0, 0))
            rip_rect = rip_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 3))
            
            small_font = pygame.font.Font(None, 36)
            level_text = small_font.render(f"Level {self.status.level} {self.status.name}", True, (255, 255, 255))
            level_rect = level_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            
            depth_text = small_font.render(f"Killed on dungeon Floor {self.status.level}", True, (255, 255, 255))
            depth_rect = depth_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 40))
            
            restart_text = small_font.render("Press ENTER to Restart", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(screen.get_width() // 2, screen.get_height() * 3 // 4))
            
            # 死亡画面の表示
            screen.fill((0, 0, 0))  # 画面を黒でクリア
            screen.blit(rip_text, rip_rect)
            screen.blit(level_text, level_rect)
            screen.blit(depth_text, depth_rect)
            screen.blit(restart_text, restart_rect)
            pygame.display.flip()
            
            # ENTERキー入力待ち
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                            waiting = False
                    elif event.type == pygame.QUIT:  # ウィンドウの×ボタン
                        pygame.quit()
                        sys.exit()
                pygame.time.wait(10)
            
            # ゲームを再スタート
            game.restart_game(self)

        else:  # 敵の場合
            # 経験値の計算と付与
            exp_gain = self.calculate_exp_reward()
            player = game.get_player()
            if player:
                player.gain_experience(exp_gain)
                self.add_logger(f"{self.status.name} was defeated! Gained {exp_gain} experience!")
            
            # 敵の削除処理
            game.remove_entity(self)

    def calculate_exp_reward(self):
        """経験値報酬の計算"""
        import random
        base_exp = self.status.level * 10  # 基本経験値
        variance = random.randint(-5, 5)    # ±5の変動
        bonus = 0
        
        # ボーナス経験値の計算（オプション）
        if hasattr(self.status, 'is_boss') and self.status.is_boss:
            bonus = 50  # ボス敵の場合のボーナス
        elif hasattr(self.status, 'is_rare') and self.status.is_rare:
            bonus = 30  # レア敵の場合のボーナス
            
        return max(1, base_exp + variance + bonus)  # 最低1は保証

    def on_death(self):
        """プレイヤーの死亡時の処理"""
        self.add_logger(f"{self.status.name} is out of power...")
        self.level_down()  # レベルダウン
        
        # HP回復（最大HPの半分）
        self.status.current_hp = max(1, self.status.max_hp // 2)
        
        # その他のペナルティ
        self.status.exp = 0  # 経験値リセット
        self.sate_hunger(-const.STOMACHSIZE // 2)  # 満腹度半減
        
        self.add_logger("You crawled back from the brink of death...")

    def handle_player_death(self):
        """ゲームクラスで実装するプレイヤー死亡時の処理"""
        # プレイヤーの位置を安全な場所に移動
        self.teleport_entity(self.player)
        
        # 状態異常をクリア
        self.player.effects.clear()
        
        # ゲーム状態の更新
        self.is_player_turn = True
        self.update_fov()

    def get_effect_info(self):
        """現在のエフェクト情報を簡略化して取得"""
        effect_symbols = []
        for effect in self.effects:
            if isinstance(effect, RegenerationEffect):
                effect_symbols.append("R")
            elif isinstance(effect, StrengthEffect):
                effect_symbols.append("S")
            elif isinstance(effect, ProtectionEffect):
                effect_symbols.append("P")
        if self.is_invisible:
            effect_symbols.append("I")  # 透明状態を表示
        return effect_symbols
