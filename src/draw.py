import pygame
import utils.constants as const
from status import Status
from player import Player
from character import Character
from inventory import Inventory


class Draw:
    def __init__(self, screen, assets_manager, game_map):
        self.screen = screen
        self.assets_manager = assets_manager
        self.game_map_font = assets_manager.load_font(const.FONT_DEFAULT, const.FONT_SIZE)
        self.log_font = assets_manager.load_font(const.FONT_DEFAULT, const.LOG_FONT_SIZE)
        self.game_map = game_map

    def draw_game_map(self):
        width, height = self.get_game_map_size_px()
        self.draw_window(0, 5, width, height)
        for y in range(len(self.game_map.tiles)):
            for x in range(len(self.game_map.tiles[y])):
                if self.game_map.explored[y][x]:
                    tile_char = self.game_map.get_tile(x, y)
                    tile_text = self.game_map_font.render(tile_char, True, "gray")
                    self.screen.blit(tile_text, (x * const.GRID_SIZE, y * const.GRID_SIZE))

    def draw_entity(self, entities_list):
        player = None

        # すべてのエンティティを描画（プレイヤーを除く）
        for entities in entities_list:
            for entity in entities:
                if isinstance(entity, Player):
                    player = entity
                else:
                    self.draw_single_entity(entity)

        # プレイヤーが存在する場合、最後にプレイヤーを描画
        if player:
            self.draw_single_entity(player)

    def draw_single_entity(self, entity, is_player=False):
        pixel_pos = (entity.x * const.GRID_SIZE, entity.y * const.GRID_SIZE)

        try:
            if self.game_map.explored[entity.y][entity.x] or is_player:
                # エンティティの領域を黒で塗りつぶす
                rect = pygame.Rect(pixel_pos, (const.GRID_SIZE, const.GRID_SIZE))
                pygame.draw.rect(self.screen, const.PYGAME_COLOR_BLACK, rect)

                # エンティティを描画
                entity_text = self.game_map_font.render(entity.char, True, entity.color)
                self.screen.blit(entity_text, pixel_pos)
        except Exception as e:
            print("FAIL: ", entity, entity.x, entity.y, entity.color, "e: ", e)

    def draw_window(
        self,
        x,
        y,
        width,
        height,
        border_color=const.PYGAME_COLOR_WHITE,
        border_width=1,
        background_color=const.PYGAME_COLOR_BLACK,
    ):
        pygame.draw.rect(self.screen, background_color, (x, y, width, height))
        pygame.draw.rect(self.screen, border_color, (x, y, width, height), border_width)

    def draw_window_with_logs(
        self,
        x,
        y,
        width,
        height,
        logs,
        border_color=const.PYGAME_COLOR_WHITE,
        border_width=1,
        background_color=const.PYGAME_COLOR_BLACK,
        font=const.FONT_DEFAULT,
        font_size=const.LOG_FONT_SIZE,
    ):
        self.draw_window(x, y, width, height, border_color, border_width, background_color)

        log_font = self.assets_manager.load_font(font, font_size)
        log_x = x + border_width
        log_y = y + border_width
        for log in logs:
            log_text = log_font.render(log, True, const.PYGAME_COLOR_WHITE)
            self.screen.blit(log_text, (log_x + 5, log_y + 5))
            log_y += log_font.get_height()  # 次のログのY座標を更新

            # ウィンドウの高さを超えたら描画を停止
            if log_y + log_font.get_height() > y + height:
                break

    def get_game_map_size(self):
        map_height = len(self.game_map.tiles)
        map_width = len(self.game_map.tiles[0])
        return map_width, map_height

    def get_game_map_size_px(self):
        map_height = len(self.game_map.tiles) * const.GRID_SIZE
        map_width = len(self.game_map.tiles[0]) * const.GRID_SIZE
        return map_width, map_height

    def draw_log_window(self, logs, n=const.DRAW_LOG_SIZE):
        x, y = self.get_game_map_size_px()
        window_width = x
        window_height = const.WINDOW_SIZE_H - y
        self.draw_window_with_logs(0, y, window_width, window_height, logs[-n:])  # 最新のn個のログを描画

    def draw_status_window(self, status: Status):
        status_txt = status.generate_status_txt()
        x, y = self.get_game_map_size_px()
        window_width = const.WINDOW_SIZE_W - x
        window_height = const.WINDOW_SIZE_H
        self.draw_window_with_logs(x, 0, window_width, window_height, status_txt, font_size=const.LOG_FONT_SIZE)

    def draw_inventory_window(self, character: Character):
        inventory_txt = character.get_inventory_str_list()
        x, y = self.get_game_map_size_px()
        window_width = const.WINDOW_SIZE_W - x
        window_height = const.WINDOW_SIZE_H
        status_window_height = const.FONT_SIZE * 8
        self.draw_window_with_logs(x, status_window_height, window_width, window_height, inventory_txt, font_size=16)
