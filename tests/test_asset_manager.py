import unittest
from unittest.mock import patch
from pathlib import Path
from assets_manager import AssetsManager

class TestAssetsManager(unittest.TestCase):
    def setUp(self):
        self.assets_manager = AssetsManager(base_path='/fake/path')

    @patch('assets_manager.Path')
    def test_get_font_path(self, mock_path):
        # モックのPathオブジェクトを設定
        mock_path.return_value = Path('/fake/path')
        # テスト対象のメソッドを実行
        result = self.assets_manager.get_font_path('example_font.ttf')
        # 期待されるパスが生成されているかを確認
        self.assertEqual(result, Path('/fake/path/assets/fonts/example_font.ttf'))

    @patch('assets_manager.Path')
    def test_get_chara_path(self, mock_path):
        mock_path.return_value = Path('/fake/path')
        result = self.assets_manager.get_chara_path('chara_data.yaml')
        self.assertEqual(result, Path('/fake/path/assets/data/chara/chara_data.yaml'))

    @patch('assets_manager.Path')
    def test_get_enemy_path(self, mock_path):
        mock_path.return_value = Path('/fake/path')
        result = self.assets_manager.get_enemy_path('enemy_data.yaml')
        self.assertEqual(result, Path('/fake/path/assets/data/enemy/enemy_data.yaml'))

    @patch('assets_manager.Path')
    def test_get_item_path(self, mock_path):
        mock_path.return_value = Path('/fake/path')
        result = self.assets_manager.get_item_path('item_data.yaml')
        self.assertEqual(result, Path('/fake/path/assets/data/item/item_data.yaml'))

    @patch('assets_manager.Path')
    def test_get_all_enemy_paths(self, mock_path):
        mock_path.return_value = Path('/fake/path')
        result = self.assets_manager.get_all_enemy_paths()
        self.assertIsInstance(result, list)
        self.assertTrue(all(isinstance(item, Path) for item in result))

if __name__ == '__main__':
    unittest.main()
