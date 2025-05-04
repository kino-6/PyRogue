from dataclasses import dataclass, field
from typing import Dict, Tuple
import os

@dataclass
class GameConstants:
    """Game constants and configuration."""
    
    # Window settings
    WINDOW_WIDTH: int = 1280
    WINDOW_HEIGHT: int = 720
    FPS: int = 60
    TURN_WAIT_MS: int = 30
    
    # Map settings
    GRID_SIZE: int = 20  # [px]
    MAP_WIDTH: int = 48  # [size]
    MAP_HEIGHT: int = 28  # [size]
    
    # Display settings
    FONT_DEFAULT: str = "CourierPrime-Regular.ttf"
    FONT_SIZE: int = 26
    LOG_FONT_SIZE: int = 20
    LOG_WRAP_SIZE: int = 57
    LOG_MESSAGE_COUNT: int = 7
    LOG_MARGIN: int = 20
    
    # Border color thresholds
    BORDER_HP_CRITICAL_THRESHOLD: float = 1/8  # HPが1/8以下の場合に赤枠
    BORDER_HP_WARNING_THRESHOLD: float = 1/2    # HPが半分以下の場合に黄枠
    
    # food
    EACH_TURN_STARVE = 1
    HUNGERTIME = 1300
    FOOD_TUNE_VALUE = 200
    FOOD_RAND_MAX = 400
    STOMACHSIZE = 2000
    STARVETIME = 850

    # File paths
    ASSETS_DIR: str = 'assets'
    DATA_DIR: str = 'data'
    CHARA_DIR: str = 'chara'
    ITEMS_DIR: str = 'items'
    FONTS_DIR: str = 'fonts'
    
    @classmethod
    def get_font_path(cls) -> str:
        """Get the path to font file."""
        return os.path.join("..", cls.ASSETS_DIR, cls.FONTS_DIR, cls.FONT_DEFAULT)
    
    @classmethod
    def get_player_config_path(cls) -> str:
        """Get the path to player configuration file."""
        return f"{cls.ASSETS_DIR}/{cls.DATA_DIR}/{cls.CHARA_DIR}/player.yaml"
        
    @classmethod
    def get_enemy_config_path(cls, enemy_name: str) -> str:
        """Get the path to enemy configuration file."""
        return f"{cls.ASSETS_DIR}/{cls.DATA_DIR}/{cls.CHARA_DIR}/enemy/{enemy_name}.yaml"
        
    @classmethod
    def get_item_config_path(cls, item_name: str) -> str:
        """Get the path to item configuration file."""
        return f"{cls.ASSETS_DIR}/{cls.DATA_DIR}/{cls.ITEMS_DIR}/{item_name}.yaml" 