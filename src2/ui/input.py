import pygame
from typing import Dict, Callable, Optional
from core.state import GameState, GameStateType

class InputHandler:
    """Handles user input and maps it to game actions."""
    
    def __init__(self):
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
            pygame.K_SPACE: 'wait',
            pygame.K_g: 'pickup',
            pygame.K_d: 'drop',
            pygame.K_u: 'use',
            pygame.K_t: 'throw',
            pygame.K_l: 'look',
            pygame.K_SLASH: 'help'
        }
        
        self.action_handlers: Dict[str, Callable] = {}
        
    def register_handler(self, action: str, handler: Callable) -> None:
        """Register a handler for a specific action."""
        self.action_handlers[action] = handler
        
    def handle_event(self, event: pygame.event.Event, game_state: GameState) -> bool:
        """Handle a pygame event and return True if the game should continue."""
        if event.type == pygame.QUIT:
            return False
            
        if event.type == pygame.KEYDOWN:
            action = self.keymap.get(event.key)
            if action and action in self.action_handlers:
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