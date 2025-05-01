import pygame
import constants as const
from status import Status
from player import Player
from character import Character
from inventory import Inventory
from stair import Stairs


class Draw:
    def __init__(self, screen, assets_manager, game_map, game):
        self.screen = screen
        self.assets_manager = assets_manager
        self.game_map_font = assets_manager.load_font(const.FONT_DEFAULT, const.FONT_SIZE)
        self.log_font = assets_manager.load_font(const.FONT_DEFAULT, const.LOG_FONT_SIZE)
        self.game_map = game_map
        self.game = game

    def draw_game_map(self):
        width, height = self.get_game_map_size_px()
        log_font = self.assets_manager.load_font(const.FONT_DEFAULT, const.LOG_FONT_SIZE)
        log_window_height = log_font.get_height() * const.DRAW_LOG_SIZE + 10

        map_height = const.WINDOW_SIZE_H - log_window_height  # 画面全体の高さからログウィンドウ分を引く

        self.draw_window(0, 5, width, map_height)
        for y in range(len(self.game_map.tiles)):
            for x in range(len(self.game_map.tiles[y])):
                pixel_y = y * const.GRID_SIZE
                if pixel_y + const.GRID_SIZE > map_height:
                    continue
                if self.game_map.explored[y][x]:
                    tile_char = self.game_map.get_tile(x, y)
                    tile_text = self.game_map_font.render(tile_char, True, "gray")
                    self.screen.blit(tile_text, (x * const.GRID_SIZE, pixel_y))

    def draw_entity(self, entities_list):
        items = []
        enemies = []
        player = None
        stairs = []

        from player import Player
        from enemy import Enemy
        from item import Item

        # すべてのエンティティを分類
        for entities in entities_list:
            for entity in entities:
                if isinstance(entity, Player):
                    player = entity
                elif isinstance(entity, Enemy):
                    enemies.append(entity)
                elif isinstance(entity, Item):
                    items.append(entity)
                elif isinstance(entity, Stairs):
                    stairs.append(entity)
                else:
                    # その他のエンティティ（必要なら追加）
                    pass

        # 1. アイテムを先に描画
        for item in items:
            self.draw_single_entity(item)
        # 2. 敵を描画
        for enemy in enemies:
            self.draw_single_entity(enemy)
            if player and enemy.can_see_player(self.game):
                self.draw_attention_mark(enemy)
        # 3. 階段を描画
        for stair in stairs:
            self.draw_single_entity(stair)
        # 4. 最後にプレイヤーを描画
        if player:
            self.draw_single_entity(player, is_player=True)

    def draw_single_entity(self, entity, is_player=False, enemy_search_active=False, is_enemy=False):
        pixel_pos = (entity.x * const.GRID_SIZE, entity.y * const.GRID_SIZE)
        try:
            # 敵サーチ中は敵だけは未踏破でも描画
            if (self.game_map.explored[entity.y][entity.x] or is_player or (enemy_search_active and is_enemy)):
                rect = pygame.Rect(pixel_pos, (const.GRID_SIZE, const.GRID_SIZE))
                pygame.draw.rect(self.screen, const.PYGAME_COLOR_BLACK, rect)

                color = "yellow" if (enemy_search_active and is_enemy) else entity.color
                entity_text = self.game_map_font.render(entity.char, True, color)
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
        log_colors,
        border_color=const.PYGAME_COLOR_WHITE,
        border_width=1,
        background_color=const.PYGAME_COLOR_BLACK,
        font=const.FONT_DEFAULT,
        font_size=const.LOG_FONT_SIZE,
    ):
        self.draw_window(x, y, width, height, border_color, border_width, background_color)

        log_font = self.assets_manager.load_font(font, font_size)
        log_y = y + border_width + 5
        max_log_height = y + height

        for log, color in zip(logs, log_colors):
            wrapped_lines = self.wrap_text(log, log_font, width - 10)  # 余白分引く
            for line in wrapped_lines:
                if log_y + log_font.get_height() > max_log_height:
                    return  # ウィンドウを超えたら終了
                log_text = log_font.render(line, True, color)
                self.screen.blit(log_text, (x + 5, log_y))
                log_y += log_font.get_height()

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

        log_font = self.assets_manager.load_font(const.FONT_DEFAULT, const.LOG_FONT_SIZE)
        font_height = log_font.get_height()
        window_height = font_height * n + 10

        # 画面全体の高さからログウィンドウの高さを引いた位置に表示
        window_y = const.WINDOW_SIZE_H - window_height

        # 折り返しを考慮して、下からn行分だけを表示
        wrapped_lines = []
        log_colors = []
        for log, color in zip(reversed(logs), reversed(["white"] * len(logs))):
            lines = self.wrap_text(log, log_font, window_width - 10)
            for line in reversed(lines):
                wrapped_lines.insert(0, (line, color))
                if len(wrapped_lines) >= n:
                    break
            if len(wrapped_lines) >= n:
                break

        # wrapped_linesは最新が下に来るように並んでいる
        display_lines = wrapped_lines[-n:]

        # 描画
        self.draw_window(0, window_y, window_width, window_height)
        log_y = window_y + 5
        for line, color in display_lines:
            log_text = log_font.render(line, True, color)
            self.screen.blit(log_text, (5, log_y))
            log_y += font_height

    def draw_status_window(self, status: Status):
        x, y = self.game.get_player_position()
        status_txt = status.generate_status_txt(x, y)
        
        # エフェクト情報を追加
        player = self.game.get_player()
        effect_symbols = player.get_effect_info()
        if effect_symbols:
            status_txt.append(f"Effects: {''.join(effect_symbols)}")
        
        log_colors = ["white"] * len(status_txt)

        x, y = self.get_game_map_size_px()
        window_width = const.WINDOW_SIZE_W - x
        window_height = const.WINDOW_SIZE_H
        status_window_height = const.FONT_SIZE * 12

        # ステータスウィンドウの位置を調整
        self.draw_window_with_logs(
            x, 0, window_width, status_window_height, status_txt, log_colors, font_size=const.LOG_FONT_SIZE - 3
        )

    def draw_inventory_window(self, character: Character):
        inventory_txt, is_defined_list = character.get_inventory_str_list()
        log_colors = ["darkgoldenrod2" if not is_defined else "white" for is_defined in is_defined_list]

        x, y = self.get_game_map_size_px()
        window_width = const.WINDOW_SIZE_W - x
        window_height = const.WINDOW_SIZE_H
        status_window_height = const.FONT_SIZE * 8

        self.draw_window_with_logs(
            x, status_window_height, window_width, window_height, inventory_txt, log_colors, font_size=16
        )

    def wrap_text(self, text, font, max_width):
        """テキストをmax_widthで折り返し、行リストで返す"""
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def draw_help_window(self, keymap):
        help_lines = []
        for action, keys in keymap.items():
            key_names = ", ".join(keys)
            help_lines.append(f"{key_names}: {action}")
        self.draw_window_with_logs(50, 50, 500, 400, help_lines, ["white"]*len(help_lines))

    def draw_item_list_window(self):
        from item_manager import ItemManager
        player = self.game.get_player()

        item_manager = ItemManager()
        item_list = item_manager.get_all_items_with_unique_id()
        selected_id = self.draw_item_list_window_and_select_id(item_list)
        if selected_id:
            # 4文字IDで一致するアイテムを探す
            for entry in item_list:
                if entry["id"][:4] == selected_id:
                    item = entry["item"]
                    player.inventory.add_item(item)
                    print(f"{item.name} added to inventory")
                    break
            else:
                print("No items with that ID were found.")
        else:
            print("Canceled.")

    def draw_item_list_window_and_select_id(self, item_list, id_length=4):
        """
        item_list: List[Dict] 例: [{"id": "xxxx", "item": <Item>}, ...]
        ユーザーがIDを入力し、Enterで決定するまで待つ。
        入力されたID（str）を返す。キャンセル時はNone。
        """
        input_id = ""
        selected_id = None
        running = True

        # スクロール位置の初期化
        if not hasattr(self, 'item_list_scroll_pos'):
            self.item_list_scroll_pos = 0

        # ウィンドウの設定
        window_width = 500
        window_height = 600
        window_x = 50
        window_y = 50
        line_height = const.FONT_SIZE + 2
        margin = 10  # マージン
        header_height = 30  # ヘッダー部分の高さ
        input_height = 30  # 入力欄の高さ
        max_lines = (window_height - header_height - input_height - margin * 2) // line_height

        while running:
            # スクロール位置の制限
            self.item_list_scroll_pos = max(0, min(self.item_list_scroll_pos, len(item_list) - max_lines))

            # 表示する行の範囲を計算
            start_line = self.item_list_scroll_pos
            end_line = min(start_line + max_lines, len(item_list))

            # ウィンドウ描画
            self.draw_window(window_x, window_y, window_width, window_height)

            # ヘルプテキストの描画
            font = pygame.font.SysFont(None, 24)
            help_text = "Up/Down: Scroll, Enter: Select, ESC: Cancel"
            help_surface = font.render(help_text, True, (255, 255, 255))
            self.screen.blit(help_surface, (window_x + margin, window_y + margin))

            # アイテムリストの描画
            list_y = window_y + header_height + margin
            for i, entry in enumerate(item_list[start_line:end_line]):
                y_pos = list_y + i * line_height
                text = f"{entry['id'][:id_length]}: {entry['item'].type}: {getattr(entry['item'], 'name', str(entry['item']))}"
                text_surface = font.render(text, True, (255, 255, 255))
                self.screen.blit(text_surface, (window_x + margin, y_pos))

            # スクロールバーの描画
            if len(item_list) > max_lines:
                scrollbar_width = 5
                scrollbar_x = window_x + window_width - margin - scrollbar_width
                scrollbar_height = (max_lines / len(item_list)) * (window_height - header_height - input_height - margin * 2)
                scrollbar_y = list_y + (self.item_list_scroll_pos / len(item_list)) * (window_height - header_height - input_height - margin * 2)
                pygame.draw.rect(self.screen, const.PYGAME_COLOR_WHITE,
                               (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))

            # 入力欄の描画
            input_y = window_y + window_height - input_height - margin
            input_surface = font.render("ID: " + input_id, True, (255, 255, 255), (0, 0, 0))
            self.screen.blit(input_surface, (window_x + margin, input_y))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                        selected_id = input_id
                        running = False
                    elif event.key == pygame.K_ESCAPE:
                        selected_id = None
                        running = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_id = input_id[:-1]
                    elif event.key == pygame.K_UP:
                        self.item_list_scroll_pos = max(0, self.item_list_scroll_pos - 1)
                    elif event.key == pygame.K_DOWN:
                        self.item_list_scroll_pos = min(len(item_list) - max_lines, self.item_list_scroll_pos + 1)
                    else:
                        if event.unicode.isprintable():
                            input_id += event.unicode
            pygame.time.wait(10)
        return selected_id

    def draw_attention_mark(self, entity):
        from constants import GRID_SIZE, PYGAME_COLOR_RED, FONT_DEFAULT
        # フォントサイズを大きめに
        font_size = max(14, GRID_SIZE // 2)
        # 太字フォントを取得（pygame.font.Fontはbold引数がないのでset_boldを使う）
        font = self.assets_manager.load_font(FONT_DEFAULT, font_size)
        font.set_bold(True)
        mark_text = font.render("!", True, PYGAME_COLOR_RED)
        # 右上隅の座標
        circle_radius = max(mark_text.get_width(), mark_text.get_height()) // 2 + 2
        # 右上隅の中心座標
        center_x = entity.x * GRID_SIZE + GRID_SIZE - circle_radius
        center_y = entity.y * GRID_SIZE + circle_radius
        center_x += GRID_SIZE // 2
        center_y -= GRID_SIZE // 2
        # 白い〇を描画
        pygame.draw.circle(self.screen, (255, 255, 255), (center_x, center_y), circle_radius)
        # !マークを〇の中心に重ねて描画
        mark_x = center_x - mark_text.get_width() // 2
        mark_y = center_y - mark_text.get_height() // 2
        self.screen.blit(mark_text, (mark_x, mark_y))
