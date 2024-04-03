import unittest
import os
import sys

from game import Game
from map import GameMap
from character import Character
from status import Status

class TestIsWalkable(unittest.TestCase):
    def get_walkable_coordinates_list(self, game_map):
        walkable_coordinates = []
        for x in range(0, game_map.width):
            for y in range(0, game_map.height):
                if game_map.is_walkable(x, y):
                    walkable_coordinates.append([x, y])
        return walkable_coordinates

    def get_not_walkable_coordinates_list(self, game_map):
        not_walkable_coordinates = []
        for x in range(0, game_map.width):
            for y in range(0, game_map.height):
                if not game_map.is_walkable(x, y):
                    not_walkable_coordinates.append([x, y])
        return not_walkable_coordinates

    def test_walkable_coordinates(self):
        game_map = GameMap()
        game = Game(game_map)
        
        walkable_coordinates = self.get_walkable_coordinates_list(game_map)
        for coord in walkable_coordinates:
            result = game.is_walkable(coord[0], coord[1])
            self.assertTrue(result, f"座標 {coord} は移動可能であるべきですが、False が返されました。")

    def generate_test_status(self):
        data = {}
        data["char"] = "@"
        data["name"] = "test"
        data["max_hp"] = 15
        data["strength"] = 8
        data["exp"] = 0
        data["level"] = 1
        data["armor"] = 0
        data["color"] = "white"
        data["exp_level"] = 1
        return data

    def test_blocked_coordinates(self):
        game_map = GameMap()
        game = Game(game_map)

        blocked_coordinates = self.get_not_walkable_coordinates_list(game_map)
        for coord in blocked_coordinates:
            status = Status(self.generate_test_status())
            character = Character(coord[0], coord[1], status)
            game.add_entity(character)  # 通行可能な床に配置したので、通行不可判定になるはず

            result = game.is_walkable(coord[0], coord[1])
            self.assertFalse(result, f"座標 {coord} は移動不可能であるべきですが、True が返されました。")

if __name__ == '__main__':
    unittest.main()