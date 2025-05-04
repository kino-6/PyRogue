import pygame
from typing import Dict, Callable, Optional
from core.state import GameState, GameStateType
import yaml
import os
import time

KEY_NAME_TO_CODE = {
    'K_UP': pygame.K_UP,
    'K_DOWN': pygame.K_DOWN,
    'K_LEFT': pygame.K_LEFT,
    'K_RIGHT': pygame.K_RIGHT,
    'K_KP8': pygame.K_KP8,
    'K_KP2': pygame.K_KP2,
    'K_KP4': pygame.K_KP4,
    'K_KP6': pygame.K_KP6,
    'K_KP7': pygame.K_KP7,
    'K_KP9': pygame.K_KP9,
    'K_KP1': pygame.K_KP1,
    'K_KP3': pygame.K_KP3,
    'K_KP5': pygame.K_KP5,
    'K_PERIOD': pygame.K_PERIOD,
    'K_LESS': pygame.K_LESS,
    'K_KP_PERIOD': pygame.K_KP_PERIOD,
    'K_e': pygame.K_e,
    'K_w': pygame.K_w,
    'K_p': pygame.K_p,
    'K_i': pygame.K_i,
    'K_F1': pygame.K_F1,
    'K_F2': pygame.K_F2,
    'K_F12': pygame.K_F12,
    'K_AT': pygame.K_AT if hasattr(pygame, 'K_AT') else 64,  # fallback for '@'
    'K_QUESTION': pygame.K_QUESTION if hasattr(pygame, 'K_QUESTION') else 63,  # fallback for '?'
    'K_SLASH': pygame.K_SLASH,
    'K_SPACE': pygame.K_SPACE,
    'K_RETURN': pygame.K_RETURN,
    'K_ESCAPE': pygame.K_ESCAPE,
    # add more as needed
}

def load_keymap_from_yaml(yaml_path: str) -> Dict[int, str]:
    if not os.path.exists(yaml_path):
        return {}
    with open(yaml_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    keymap = config.get('keymap', {})
    result = {}
    for action, keys in keymap.items():
        for key in keys:
            code = KEY_NAME_TO_CODE.get(key)
            if code is not None:
                result[code] = action
    return result

class InputHandler:
    """Handles user input and maps it to game actions, including key repeat."""
    
    def __init__(self, config_path: Optional[str] = None):
        # Load keymap from config.yaml if available, else use default
        loaded_keymap = load_keymap_from_yaml(config_path) if config_path else {}
        if loaded_keymap:
            self.keymap: Dict[int, str] = loaded_keymap
        else:
            self.keymap: Dict[int, str] = {
                pygame.K_UP: 'move_up',
                pygame.K_DOWN: 'move_down',
                pygame.K_LEFT: 'move_left',
                pygame.K_RIGHT: 'move_right',
                pygame.K_KP8: 'move_up',
                pygame.K_KP2: 'move_down',
                pygame.K_KP4: 'move_left',
                pygame.K_KP6: 'move_right',
                pygame.K_KP7: 'move_up_left',
                pygame.K_KP9: 'move_up_right',
                pygame.K_KP1: 'move_down_left',
                pygame.K_KP3: 'move_down_right',
                pygame.K_i: 'inventory',
                pygame.K_ESCAPE: 'cancel',
                pygame.K_RETURN: 'confirm',
                pygame.K_d: 'drop',
                pygame.K_t: 'throw',
                pygame.K_SLASH: 'help',
                pygame.K_PERIOD: 'descend_stairs',
                pygame.K_LESS: 'descend_stairs',
                pygame.K_KP_PERIOD: 'descend_stairs',
                pygame.K_r: 'rest',
                pygame.K_KP5: 'rest',
                pygame.K_e: 'eat_food',
                pygame.K_w: 'wear_armor',
                pygame.K_p: 'put_on_a_ring',
            }
        self.action_handlers: Dict[str, Callable] = {}
        self.last_key_time: Dict[int, float] = {}
        self.key_repeat_interval: float = 0.1  # seconds
    
    def register_handler(self, action: str, handler: Callable) -> None:
        """Register a handler for a specific action."""
        self.action_handlers[action] = handler
    
    def handle_event(self, event: pygame.event.Event, game_state: GameState) -> bool:
        """Handle a pygame event and return True if the game should continue."""
        if event.type == pygame.QUIT:
            return False
        
        # Handle KEYDOWN events (single press)
        if event.type == pygame.KEYDOWN:
            action = self.keymap.get(event.key)
            print(f"ACTION: {action}")
            if action and action in self.action_handlers:
                self.action_handlers[action](game_state)
                self.last_key_time[event.key] = time.time()
        
        # Handle key repeat (hold)
        keys = pygame.key.get_pressed()
        current_time = time.time()
        for key, action in self.keymap.items():
            if keys[key]:
                last_time = self.last_key_time.get(key, 0)
                if current_time - last_time > self.key_repeat_interval:
                    self.last_key_time[key] = current_time
                    if action in self.action_handlers:
                        self.action_handlers[action](game_state)
        
        return True
    
    def get_direction(self, key: int) -> Optional[tuple[int, int]]:
        """Convert a key to a direction vector."""
        directions = {
            pygame.K_UP: (0, -1),
            pygame.K_DOWN: (0, 1),
            pygame.K_LEFT: (-1, 0),
            pygame.K_RIGHT: (1, 0),
            pygame.K_KP8: (0, -1),  # Numpad
            pygame.K_KP2: (0, 1),
            pygame.K_KP4: (-1, 0),
            pygame.K_KP6: (1, 0),
            pygame.K_KP7: (-1, -1),  # Diagonals
            pygame.K_KP9: (1, -1),
            pygame.K_KP1: (-1, 1),
            pygame.K_KP3: (1, 1)
        }
        return directions.get(key)
    
    def wait_for_key(self) -> Optional[int]:
        """Wait for a key press and return the key code."""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    return event.key
            pygame.time.wait(100)
    
    def wait_for_direction(self) -> Optional[tuple[int, int]]:
        """Wait for a direction key press and return the direction vector."""
        while True:
            key = self.wait_for_key()
            if key is None:
                return None
            direction = self.get_direction(key)
            if direction:
                return direction
    
    def wait_for_confirm(self) -> bool:
        """Wait for confirmation (Enter) or cancellation (Escape)."""
        while True:
            key = self.wait_for_key()
            if key == pygame.K_RETURN:
                return True
            if key == pygame.K_ESCAPE:
                return False 