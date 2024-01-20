def update_position(pos, dx, dy, player_size, screen):
    width, height = screen.get_size()
    new_x = max(0, min(width - player_size[0], pos[0] + dx))
    new_y = max(0, min(height - player_size[1], pos[1] + dy))
    return [new_x, new_y]
