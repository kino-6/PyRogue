import os
import glob
import yaml
from pathlib import Path
import pygame
from typing import List


class AssetsManager:
    def __init__(self, base_path=None):
        if base_path is None:
            self.base_path = Path(__file__).parent.parent
        else:
            self.base_path = Path(base_path)

    def get_font_path(self, font_name):
        return self.base_path.joinpath('assets', 'fonts', font_name)

    def load_font(self, font_name, size):
        font_path = self.get_font_path(font_name)
        return pygame.font.Font(str(font_path), size)

    def get_chara_path(self, data_name) -> Path:
        return self.base_path.joinpath("assets", "data", "chara", data_name)

    def get_enemy_path(self, data_name) -> Path:
        return self.base_path.joinpath("assets", "data", "enemy", data_name)

    def get_all_enemy_paths(self) -> Path:
        enemy_directory = self.base_path.joinpath("assets", "data", "enemy")
        return list(enemy_directory.glob("*.yaml"))

    def get_item_path(self, data_name) -> Path:
        return self.base_path.joinpath("assets", "data", "item", data_name)

    def get_config_path(self, data_name="config") -> Path:
        return self.base_path.joinpath("assets", data_name)

    def get_item_data_list(self, data_name) -> List:
        directory = self.get_item_path(data_name)
        # print(f"directory = {directory}")
        file_paths = list(directory.glob("*.yaml"))
        # print(f"file_paths = {file_paths}")

        data_list = []
        for file_path in file_paths:
            with open(file_path, "r") as file:
                data = yaml.safe_load(file)
                data_list.append(data)
        # print(f"len(data_list) = {len(data_list)}")
        return data_list
