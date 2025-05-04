import pygame
from typing import List, Dict, Any
from core.entity import Entity
from core.state import GameState
from game.character import Character
from utils.constants import GameConstants
from core.map import GameMap

class Display:
    """Handles the rendering of the game state."""
    
    def __init__(self, width: int, height: int):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF)
        pygame.display.set_caption("PyRogue")
        
        # Load fonts
        font_path = GameConstants.get_font_path()
        try:
            self.game_map_font = pygame.font.Font(font_path, GameConstants.FONT_SIZE)
            self.log_font = pygame.font.Font(font_path, GameConstants.LOG_FONT_SIZE)
        except FileNotFoundError:
            # Fallback to default font if custom font is not found
            print(f"Warning: Font file not found at {font_path}. Using default font.")
            self.game_map_font = pygame.font.Font(None, GameConstants.FONT_SIZE)
            self.log_font = pygame.font.Font(None, GameConstants.LOG_FONT_SIZE)
        
        # Define colors
        self.colors = {
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'gray': (128, 128, 128),
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'dark_gray': (64, 64, 64)
        }
        
        # Define tile sizes
        self.tile_width = GameConstants.GRID_SIZE
        self.tile_height = GameConstants.GRID_SIZE
        
        # Layout sizes
        self.map_width_px = GameConstants.MAP_WIDTH * self.tile_width
        self.map_height_px = GameConstants.MAP_HEIGHT * self.tile_height
        self.log_height_px = self.log_font.get_height() * GameConstants.LOG_MESSAGE_COUNT + 10
        self.status_height_px = GameConstants.FONT_SIZE * 10 + 10
        self.inventory_height_px = height - self.status_height_px
        self.right_panel_width = width - self.map_width_px
        
    def draw_game_state(self, game_state: GameState) -> None:
        """Draw the entire game state."""
        self.screen.fill(self.colors['black'])
        
        # Draw map window (top-left)
        self.draw_window(0, 0, self.map_width_px, self.map_height_px, self.colors['white'], 2)
        self.draw_map(game_state.game_map)
        for pos, entities in game_state.entities.items():
            x, y = pos
            for entity in entities:
                self.draw_entity(entity, x, y)
        
    def draw_status(self, character: Character) -> None:
        """Draw character status (top-right)."""
        border_color = self.colors['white']
        if character.status.current_hp > 0:
            hp_ratio = character.status.current_hp / character.status.max_hp
            if hp_ratio <= GameConstants.BORDER_HP_CRITICAL_THRESHOLD:
                border_color = self.colors['red']
            elif hp_ratio <= GameConstants.BORDER_HP_WARNING_THRESHOLD:
                border_color = self.colors['yellow']
        status_text = [
            f"Name: {character.status.name}, ({character.x}, {character.y})",
            f"Floor: {character.status.level}, {character.status.turn} turns",
            f"Gold: {character.status.gold}",
            f"Hp: {character.status.current_hp}/{character.status.max_hp}",
            f"Str: {character.status.attack}",
            f"Ac: {character.status.defense}",
            f"ExpLv: {character.status.level}",
            f"Exp: {character.status.experience} / {character.status.next_level_exp}",
            f"Food: {character.status.food_left} %"
        ]
        self.draw_window_with_logs(
            self.map_width_px, 0, self.right_panel_width, self.status_height_px,
            status_text, [self.colors['white']] * len(status_text),
            border_color=border_color, border_width=2
        )
        
    def draw_inventory(self, inventory_lines: List[str], highlight_indices: List[int] = None) -> None:
        """Draw inventory (bottom-right)."""
        if highlight_indices is None:
            highlight_indices = []
        log_colors = [self.colors['yellow'] if i in highlight_indices else self.colors['white'] for i in range(len(inventory_lines))]
        self.draw_window_with_logs(
            self.map_width_px, self.status_height_px, self.right_panel_width, self.inventory_height_px,
            inventory_lines, log_colors,
            border_color=self.colors['white'], border_width=2
        )
        
    def draw_messages(self, messages: List[str]) -> None:
        """Draw game messages (bottom-left)."""
        y = GameConstants.WINDOW_HEIGHT - self.log_height_px
        self.draw_window_with_logs(
            0, y, self.map_width_px, self.log_height_px,
            messages, [self.colors['white']] * len(messages),
            border_color=self.colors['white'], border_width=2,
            extra_margin=5
        )
        
    def draw_map(self, game_map) -> None:
        """Draw the game map in roguelike ASCII style."""
        tile_chars = {
            game_map.WALL_HORIZONTAL: (game_map.WALL_HORIZONTAL, self.colors['gray']),
            game_map.WALL_VERTICAL: (game_map.WALL_VERTICAL, self.colors['gray']),
            game_map.WALL_FLOOR: (game_map.WALL_FLOOR, self.colors['white']),
            game_map.WALL_DOOR: (game_map.WALL_DOOR, self.colors['yellow']),
            game_map.WALL_PASSAGE: (game_map.WALL_PASSAGE, self.colors['white']),
            game_map.WALL_STAIRS: (game_map.WALL_STAIRS, self.colors['white']),
            game_map.WALL_ITEM: (game_map.WALL_ITEM, self.colors['red'])
        }
        for y in range(1, game_map.height - 1):
            for x in range(1, game_map.width - 1):
                tile = game_map.tiles[y, x]
                char, color = tile_chars.get(tile, (tile, self.colors['white']))
                if not game_map.is_explored(x, y):
                    continue
                text = self.game_map_font.render(char, True, color)
                self.screen.blit(text, (x * self.tile_width, y * self.tile_height))
        # Entities (player, items, etc.) are drawn separately in draw_entity
        
    def draw_entity(self, entity: Entity, x: int, y: int) -> None:
        """Draw an entity at the given position."""
        if isinstance(entity, Character):
            color = self.colors['red'] if not entity.is_alive else self.colors['green']
        else:
            color = self.colors['white']
            
        # Draw entity background
        pygame.draw.rect(
            self.screen,
            self.colors['black'],
            (x * self.tile_width, y * self.tile_height,
             self.tile_width, self.tile_height)
        )
        
        # Draw entity character
        text = self.game_map_font.render(entity.display_name, True, color)
        self.screen.blit(text, (x * self.tile_width, y * self.tile_height))
        
    def draw_window(self, x: int, y: int, width: int, height: int,
                   border_color: tuple, border_width: int = 1,
                   background_color: tuple = None) -> None:
        """Draw a window with border."""
        if background_color is None:
            background_color = self.colors['black']
            
        # Draw background
        pygame.draw.rect(self.screen, background_color, (x, y, width, height))
        # Draw border
        pygame.draw.rect(self.screen, border_color, (x, y, width, height), border_width)
        
    def draw_window_with_logs(self, x: int, y: int, width: int, height: int,
                            logs: List[str], log_colors: List[tuple],
                            border_color: tuple, border_width: int = 1,
                            extra_margin: int = 0) -> None:
        """Draw a window with logs."""
        self.draw_window(x, y, width, height, border_color, border_width)
        
        # Draw logs
        log_y = y + border_width + extra_margin
        for log, color in zip(logs, log_colors):
            if log_y + self.log_font.get_height() > y + height - extra_margin:
                break
            text = self.log_font.render(log, True, color)
            self.screen.blit(text, (x + 5, log_y))
            log_y += self.log_font.get_height()
        
    def clear(self) -> None:
        """Clear the screen."""
        self.screen.fill(self.colors['black'])
        
    def update(self) -> None:
        """Update the display."""
        pygame.display.flip()
        
    def quit(self) -> None:
        """Clean up display resources."""
        pygame.quit() 