from core.map import GameMap
from core.state import GameState
from utils.config_loader import ConfigLoader
from game.chara_builder import build_player
from utils.constants import GameConstants
import numpy as np

def initialize_game(seed: int = 42):
    config_loader = ConfigLoader()
    rng = np.random.default_rng(seed)
    game_map = GameMap(GameConstants.MAP_WIDTH, GameConstants.MAP_HEIGHT, rng)
    player_config = config_loader.load_player_config()
    # Use player_start if available
    if hasattr(game_map, 'player_start') and game_map.player_start:
        px, py = game_map.player_start
    else:
        px, py = GameConstants.MAP_WIDTH // 2, GameConstants.MAP_HEIGHT // 2
    player = build_player(player_config, px, py)
    game_state = GameState(game_map)
    game_state.add_entity(player)
    return game_state, player, config_loader
