from ui.input import InputHandler
import pygame
import time

def create_input_handler(game_state, player, logger):
    input_handler = InputHandler(config_path="assets/config/config.yaml")

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

    def handle_descend_stairs(_):
        x, y = player.x, player.y
        tile = game_state.game_map.tiles[y, x]
        if tile == game_state.game_map.WALL_STAIRS:
            # 新しい階層を生成
            new_map = type(game_state.game_map)(game_state.game_map.width, game_state.game_map.height)
            game_state.game_map = new_map
            # --- エンティティ管理情報をリセット ---
            if hasattr(game_state, 'entities'):
                game_state.entities.clear()
            if hasattr(game_state, 'entity_positions'):
                game_state.entity_positions.clear()
            # プレイヤーのみ新しいマップに再配置
            if hasattr(new_map, 'player_start'):
                player.x, player.y = new_map.player_start
            else:
                player.x, player.y = new_map.width // 2, new_map.height // 2
            if hasattr(game_state, 'add_entity'):
                game_state.add_entity(player)
            logger.add_message("You descend the stairs to a new floor.", turn=player.status.turn)
        else:
            logger.add_message("There are no stairs here.", turn=player.status.turn)

    input_handler.register_handler('descend_stairs', handle_descend_stairs)

    # 他のアクションもここで登録可能
    # input_handler.register_handler('pickup', ...)

    return input_handler 

def handle_event(self, event, game_state):
    if event.type == pygame.KEYDOWN:
        print(f"KEYDOWN: {event.key}")
        action = self.keymap.get(event.key)
        print(f"Resolved action: {action}")
        if action and action in self.action_handlers:
            print(f"Calling handler for: {action}")
            self.action_handlers[action](game_state)
            self.last_key_time[event.key] = time.time() 