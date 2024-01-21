import pygame
import utils.constants as const
from enemy import Enemy


class InputHandler:
    def __init__(self, movement_speed, game, game_map):
        self.movement_speed = movement_speed
        self.game = game
        self.game_map = game_map
        self.dx = 0
        self.dy = 0

    def handle_keys(self, player_pos):
        keys = pygame.key.get_pressed()
        mods = pygame.key.get_mods()  # 現在押されている修飾キーを取得
        self.dx, self.dy = 0, 0

        # 水平方向の移動
        if keys[pygame.K_LEFT] or keys[pygame.K_KP4]:
            self.dx -= self.movement_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_KP6]:
            self.dx += self.movement_speed

        # 垂直方向の移動
        if keys[pygame.K_UP] or keys[pygame.K_KP8]:
            self.dy -= self.movement_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_KP2]:
            self.dy += self.movement_speed

        # 斜め方向の移動
        if keys[pygame.K_KP7]:
            self.dx, self.dy = -self.movement_speed, -self.movement_speed
        if keys[pygame.K_KP9]:
            self.dx, self.dy = self.movement_speed, -self.movement_speed
        if keys[pygame.K_KP1]:
            self.dx, self.dy = -self.movement_speed, self.movement_speed
        if keys[pygame.K_KP3]:
            self.dx, self.dy = self.movement_speed, self.movement_speed

        # actions
        if keys[pygame.K_PERIOD] or keys[pygame.K_GREATER]:
            self.action = ("descend_stairs", player_pos[0], player_pos[1])
        elif keys[pygame.K_KP5]:
            self.action = ("rest", player_pos[0], player_pos[1])
        elif keys[pygame.K_e]:
            self.action = ("eat_food", player_pos[0], player_pos[1])
        elif mods & pygame.KMOD_SHIFT and keys[pygame.K_w]:
            self.action = ("wear_armor", player_pos[0], player_pos[1])
        elif keys[pygame.K_w]:
            self.action = ("wield_a_weapon", player_pos[0], player_pos[1])
        else:
            # 移動先の座標を計算
            new_x = player_pos[0] + self.dx
            new_y = player_pos[1] + self.dy

            # 移動先がプレイヤーの現在の位置と異なる場合のみ、アクションを決定
            if (new_x, new_y) != player_pos:
                self.determine_action(player_pos, new_x, new_y)

        # print("mods: ", mods & pygame.KMOD_SHIFT, "w: ", keys[pygame.K_w], self.action)

    def determine_action(self, current_pos, new_x, new_y):
        # 移動先のタイルを確認
        tile = self.game_map.get_tile(new_x, new_y)
        entities_at_new_pos = self.game.entity_positions.get((new_x, new_y), [])

        if any(isinstance(entity, Enemy) for entity in entities_at_new_pos):
            self.action = ("attack", new_x, new_y)
        elif self.game_map.is_walkable(new_x, new_y) and [new_x, new_y] != current_pos:
            self.action = ("move", new_x, new_y)
        else:
            self.action = ("none", current_pos[0], current_pos[1])
