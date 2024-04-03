import pytest
from unittest.mock import patch, MagicMock
from draw import Draw

@pytest.fixture
def mock_pygame():
    with patch('draw.pygame') as mock:
        yield mock

def test_draw_game_map_calls_pygame_blit(mock_pygame):
    screen = MagicMock()
    assets_manager = MagicMock()
    game_map = MagicMock()
    game_map.tiles = [[1, 2], [3, 4]]
    game_map.explored = [[True, True], [True, True]]
    game_map.get_tile = MagicMock(return_value=' ')

    drawer = Draw(screen, assets_manager, game_map)
    drawer.draw_game_map()

    # pygameのblitメソッドが期待通りに呼び出されたか検証
    assert screen.blit.called
