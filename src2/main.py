import pygame
import sys
import os
from ui.display import Display
from ui.input import InputHandler
from utils.logger import Logger
from utils.constants import GameConstants
from utils.game_initializer import initialize_game

def main():
    # Initialize game systems
    display = Display(GameConstants.WINDOW_WIDTH, GameConstants.WINDOW_HEIGHT)
    input_handler = InputHandler()
    logger = Logger()
    
    # Use initializer to set up game state, player, and config_loader
    game_state, player, config_loader = initialize_game()
    
    # Register input handlers
    def handle_move(dx: int, dy: int):
        new_x = player.x + dx
        new_y = player.y + dy
        if game_state.move_entity(player, new_x, new_y):
            player.status.turn += 1
            logger.add_message(f"Moved to ({new_x}, {new_y})", turn=player.status.turn)
            
    input_handler.register_handler('move_up', lambda _: handle_move(0, -1))
    input_handler.register_handler('move_down', lambda _: handle_move(0, 1))
    input_handler.register_handler('move_left', lambda _: handle_move(-1, 0))
    input_handler.register_handler('move_right', lambda _: handle_move(1, 0))
    input_handler.register_handler('move_up_left', lambda _: handle_move(-1, -1))
    input_handler.register_handler('move_up_right', lambda _: handle_move(1, -1))
    input_handler.register_handler('move_down_left', lambda _: handle_move(-1, 1))
    input_handler.register_handler('move_down_right', lambda _: handle_move(1, 1))
    
    # Main game loop
    running = True
    clock = pygame.time.Clock()
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if not input_handler.handle_event(event, game_state):
                running = False
                
        # Update game state
        game_state.turn += 1
        
        # Draw game state
        display.draw_game_state(game_state)
        display.draw_status(player)
        display.draw_inventory(player.get_inventory_lines())
        display.draw_messages(logger.get_messages(GameConstants.LOG_MESSAGE_COUNT))
        display.update()
        
        # Cap the frame rate
        clock.tick(GameConstants.FPS)
        
    # Clean up
    display.quit()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 