from unittest.mock import patch, Mock, mock_open
import os
import sys
import json
import yaml

from game import Game
import pytest
from unittest.mock import Mock, patch
from game_initializer import GameInitializer


# GameInitializer クラスの setup_player メソッドのテスト
@patch('game_initializer.AssetsManager')
def test_setup_player(MockAssetsManager):
    # モックオブジェクトの設定
    mock_game = Mock()
    mock_logger = Mock()
    mock_assets_manager = MockAssetsManager.return_value
    mock_assets_manager.get_chara_path.return_value = '../src/data/player.yaml'
    
    # yaml ファイルの内容をモック化
    player_yaml_content = {
        "char": "@",
        "name": "Player",
        "max_hp": 15,
        "strength": 12,
        "exp": 0,
        "level": 1,
        "exp_level": 1,
        "armor": 0,
        "color": "white"
    }
    player_yaml_content_str = yaml.dump(player_yaml_content)

    with patch('builtins.open', mock_open(read_data=player_yaml_content_str)), \
         patch('yaml.safe_load', return_value=player_yaml_content):
        initializer = GameInitializer(mock_game, mock_logger)
        player = initializer.setup_player()
        
        mock_game.add_entity.assert_called_with(player)
        assert player.char == "@"
        assert player.status.name == "Player"
        assert player.status.max_hp == 15
        assert player.status.strength == 12
        assert player.status.exp == 0
        assert player.status.level == 1
        assert player.status.exp_level == 1
        assert player.status.armor == 0
        assert player.color == "white"
