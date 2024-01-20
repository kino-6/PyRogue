import os
import glob
import yaml
from pathlib import Path
import pygame


class AssetsManager:
    def __init__(self):
        # スクリプトのあるディレクトリの絶対パスを取得
        self.base_path = Path(__file__).parent.parent.parent

    def get_font_path(self, font_name):
        # フォントファイルへのパスを生成
        return self.base_path / "assets" / "fonts" / font_name

    def load_font(self, font_name, size):
        # フォントを読み込む
        font_path = self.get_font_path(font_name)
        return pygame.font.Font(str(font_path), size)

    def get_chara_path(self, data_name):
        return self.base_path / "assets" / "data" / "chara" / data_name

    def get_enemy_path(self, data_name):
        return self.base_path / "assets" / "data" / "enemy" / data_name

    def get_all_enemy_paths(self):
        enemy_directory = self.base_path / "assets" / "data" / "enemy"
        return list(enemy_directory.glob("*.yaml"))

    def get_item_path(self, data_name):
        return self.base_path / "assets" / "data" / "item" / data_name
