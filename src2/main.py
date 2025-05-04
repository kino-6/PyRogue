import pygame
import sys
import os
from ui.display import Display
from ui.input import InputHandler
from utils.logger import Logger
from utils.constants import GameConstants
from utils.game_initializer import initialize_game
from ui.input_setup import create_input_handler
import time
from typing import Dict, Optional

def main():
    # Initialize game systems
    display = Display(GameConstants.WINDOW_WIDTH, GameConstants.WINDOW_HEIGHT)
    logger = Logger()
    
    # Use initializer to set up game state, player, and config_loader
    game_state, player, config_loader = initialize_game()
    
    # Register input handlers
    input_handler = create_input_handler(game_state, player, logger)
    
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