import pygame
import constants as const
from enemy import Enemy
import time
from keymap_loader import load_keymap, get_action_for_key
from assets_manager import AssetsManager


class InputHandler:
    def __init__(self, movement_speed, game, game_map):
        self.movement_speed = movement_speed
        self.game = game
        self.game_map = game_map
        self.dx = 0
        self.dy = 0
        self.last_key_time = {}
        self.key_repeat_interval = 0.1
        self.action = None

        self.assets_manager = AssetsManager()
        directory = self.assets_manager.get_config_path()
        config_path = directory / "config.yaml"
        self.keymap = load_keymap(config_path)

    def handle_keys(self, player_pos):
        if self.game.in_selection_mode:
            return
        current_time = time.time()
        keys = pygame.key.get_pressed()
        mods = pygame.key.get_mods()
        self.dx, self.dy = 0, 0

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                action = get_action_for_key(event.key, mods, self.keymap)
                if action:
                    self.action = (action, player_pos[0], player_pos[1])
                    return

        # 水平方向の移動
        if keys[pygame.K_LEFT] or keys[pygame.K_KP4]:
            if self.is_time_for_repeat(pygame.K_LEFT, current_time):
                self.dx -= self.movement_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_KP6]:
            if self.is_time_for_repeat(pygame.K_RIGHT, current_time):
                self.dx += self.movement_speed

        # 垂直方向の移動
        if keys[pygame.K_UP] or keys[pygame.K_KP8]:
            if self.is_time_for_repeat(pygame.K_UP, current_time):
                self.dy -= self.movement_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_KP2]:
            if self.is_time_for_repeat(pygame.K_DOWN, current_time):
                self.dy += self.movement_speed

        # 斜め方向の移動
        if keys[pygame.K_KP7] and self.is_time_for_repeat(pygame.K_KP7, current_time):
            self.dx, self.dy = -self.movement_speed, -self.movement_speed
        if keys[pygame.K_KP9] and self.is_time_for_repeat(pygame.K_KP9, current_time):
            self.dx, self.dy = self.movement_speed, -self.movement_speed
        if keys[pygame.K_KP1] and self.is_time_for_repeat(pygame.K_KP1, current_time):
            self.dx, self.dy = -self.movement_speed, self.movement_speed
        if keys[pygame.K_KP3] and self.is_time_for_repeat(pygame.K_KP3, current_time):
            self.dx, self.dy = self.movement_speed, self.movement_speed

        # actions
        if keys[pygame.K_PERIOD] or keys[pygame.K_LESS] or keys[pygame.K_KP_PERIOD]:
            self.action = ("descend_stairs", player_pos[0], player_pos[1])
        elif keys[pygame.K_KP5]:
            self.action = ("rest", player_pos[0], player_pos[1])
        elif keys[pygame.K_e]:
            self.action = ("eat_food", player_pos[0], player_pos[1])
        elif mods & pygame.KMOD_SHIFT and keys[pygame.K_w]:
            self.action = ("wear_armor", player_pos[0], player_pos[1])
        elif keys[pygame.K_w]:
            self.action = ("wield_a_weapon", player_pos[0], player_pos[1])
        elif mods & pygame.KMOD_SHIFT and keys[pygame.K_p]:
            self.action = ("put_on_a_ring", player_pos[0], player_pos[1])
        elif keys[pygame.K_d]:
            self.action = ("drop_item", player_pos[0], player_pos[1])
        elif mods & pygame.KMOD_SHIFT and keys[pygame.K_2]:
            self.action = ("debug_mode", player_pos[0], player_pos[1])
        elif keys[pygame.K_F12]:
            self.action = ("console_mode", player_pos[0], player_pos[1])
        elif mods & pygame.KMOD_SHIFT and keys[pygame.K_h]:
            self.action = ("draw_help", player_pos[0], player_pos[1])
        elif keys[pygame.K_i]:
            self.action = ("inspect_item", player_pos[0], player_pos[1])
        elif keys[pygame.K_F1]:
            self.action = ("save_game", player_pos[0], player_pos[1])
        elif keys[pygame.K_F2]:
            self.action = ("load_game", player_pos[0], player_pos[1])
        elif keys[pygame.K_COMMA] and mods & pygame.KMOD_SHIFT:
            self.action = ("descend_stairs", player_pos[0], player_pos[1])
        elif keys[pygame.K_q]:  # 'q'キーでポーションを使用
            self.action = ("quaff_potion", *player_pos)
        else:
            # 移動先の座標を計算
            new_x = player_pos[0] + self.dx
            new_y = player_pos[1] + self.dy

            # 移動先がプレイヤーの現在の位置と異なる場合のみ、アクションを決定
            if (new_x, new_y) != player_pos:
                self.determine_action(player_pos, new_x, new_y)

    def determine_action(self, current_pos, new_x, new_y):
        # 移動先のタイルを確認
        tile = self.game_map.get_tile(new_x, new_y)
        entities_at_new_pos = self.game.entity_positions.get((new_x, new_y), [])

        if any(isinstance(entity, Enemy) for entity in entities_at_new_pos):
            self.action = ("attack", new_x, new_y)
        elif self.game_map.is_walkable(new_x, new_y) and [new_x, new_y] != current_pos:
            print(f"Action generated - walkable: {self.game_map.is_walkable(new_x, new_y)}, new_pos: {[new_x, new_y]}, current_pos: {current_pos}")
            self.action = ("move", new_x, new_y)
            print(f"Action set to: {self.action}")
        else:
            self.action = ("none", current_pos[0], current_pos[1])

    def is_time_for_repeat(self, key, current_time):
        last_time = self.last_key_time.get(key, 0)
        if current_time - last_time > self.key_repeat_interval:
            self.last_key_time[key] = current_time
            return True
        return False
