import constants as const
import random
from stair import Stairs
from entity import Entity


class GameMap:
    def __init__(self):
        self.width = const.GAMEMAP_WIDTH
        self.height = const.GAMEMAP_HEIGHT
        self.init_explored()

    def init_explored(self):
        self.explored = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.room_info = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.tiles = self.generate_dungeon()

    def generate_dungeon(self, num_rooms_range=(4, 12), room_size_range=(6, 12), max_attempts=30):
        while True:
            dungeon = [[" " for _ in range(self.width)] for _ in range(self.height)]
            rooms = []
            room_id = 0

            for _ in range(max_attempts):
                if len(rooms) >= num_rooms_range[1]:
                    break

                w = random.randint(room_size_range[0], room_size_range[1])
                h = random.randint(room_size_range[0], room_size_range[1])
                x = random.randint(1, self.width - w - 1)
                y = random.randint(1, self.height - h - 1)

                new_room = {"x1": x, "y1": y, "x2": x + w, "y2": y + h}

                if not any(self.rooms_overlap(new_room, existing_room) for existing_room in rooms):
                    self.create_room(dungeon, new_room)
                    rooms.append(new_room)

            if num_rooms_range[0] <= len(rooms) <= num_rooms_range[1]:
                break

        # 通路の生成
        for i in range(1, len(rooms)):
            self.create_passage(dungeon, rooms[i - 1], rooms[i])

        # 部屋のクリーンアップ
        for room in rooms:
            self.cleanup_room(dungeon, room)

        # ドアの生成
        for room in rooms:
            self.create_door(dungeon, room)

        # 通路と隣接していないドアを壁に戻す
        self.fix_isolated_doors(dungeon)

        for room in rooms:
            # 部屋のマスに部屋のIDを記録
            for y in range(room["y1"], room["y2"]):
                for x in range(room["x1"], room["x2"]):
                    self.room_info[y][x] = room_id
            room_id += 1

        return dungeon

    def rooms_overlap(self, room1, room2):
        # 部屋が重なっているかどうかをチェック
        return (
            room1["x1"] <= room2["x2"]
            and room1["x2"] >= room2["x1"]
            and room1["y1"] <= room2["y2"]
            and room1["y2"] >= room2["y1"]
        )

    def create_room(self, dungeon, room):
        # 上の壁と下の壁を生成
        for x in range(room["x1"], room["x2"]):
            dungeon[room["y1"]][x] = "-"
            dungeon[room["y2"] - 1][x] = "-"

        # 左の壁と右の壁を生成
        for y in range(room["y1"] + 1, room["y2"] - 1):
            dungeon[y][room["x1"]] = "|"
            dungeon[y][room["x2"] - 1] = "|"

        # 床を生成
        for y in range(room["y1"] + 1, room["y2"] - 1):
            for x in range(room["x1"] + 1, room["x2"] - 1):
                dungeon[y][x] = "."

    def create_passage(self, dungeon, room1, room2):
        # 部屋の中心点を計算
        center1 = ((room1["x1"] + room1["x2"]) // 2, (room1["y1"] + room1["y2"]) // 2)
        center2 = ((room2["x1"] + room2["x2"]) // 2, (room2["y1"] + room2["y2"]) // 2)

        # 水平方向の通路を生成
        for x in range(min(center1[0], center2[0]), max(center1[0], center2[0]) + 1):
            dungeon[center1[1]][x] = "#"

        # 垂直方向の通路を生成
        for y in range(min(center1[1], center2[1]), max(center1[1], center2[1]) + 1):
            dungeon[y][center2[0]] = "#"

    def create_door(self, dungeon, room):
        # 部屋の上下の壁を検証
        for x in range(room["x1"], room["x2"]):
            if dungeon[room["y1"]][x] == "#":
                dungeon[room["y1"]][x] = "+"
            if dungeon[room["y2"] - 1][x] == "#":
                dungeon[room["y2"] - 1][x] = "+"

        # 部屋の左右の壁を検証
        for y in range(room["y1"], room["y2"]):
            if dungeon[y][room["x1"]] == "#":
                dungeon[y][room["x1"]] = "+"
            if dungeon[y][room["x2"] - 1] == "#":
                dungeon[y][room["x2"] - 1] = "+"

    def cleanup_room(self, dungeon, room):
        # 部屋の内部をクリーンアップ（床と壁の再配置）
        for y in range(room["y1"] + 1, room["y2"] - 1):
            for x in range(room["x1"] + 1, room["x2"] - 1):
                dungeon[y][x] = "."

    def fix_isolated_doors(self, dungeon):
        width = len(dungeon[0])
        height = len(dungeon)

        for y in range(height):
            for x in range(width):
                if dungeon[y][x] == "+":
                    if not self.is_adjacent_to_passage(dungeon, x, y, width, height):
                        # ドアが通路と隣接していない場合、適切な壁に戻す
                        dungeon[y][x] = self.determine_wall_type(dungeon, x, y, width, height)

    def determine_wall_type(self, dungeon, x, y, width, height):
        # 上下左右のタイルをチェックして、適切な壁のタイプを決定
        if x > 0 and dungeon[y][x - 1] in [" ", "#"] and x < width - 1 and dungeon[y][x + 1] in [" ", "#"]:
            return "|"
        else:
            return "-"

    def is_adjacent_to_passage(self, dungeon, x, y, width, height):
        # ドアの周囲をチェックして、通路と隣接しているかどうかを判断
        adjacent_tiles = []
        if x > 0:
            adjacent_tiles.append(dungeon[y][x - 1])
        if x < width - 1:
            adjacent_tiles.append(dungeon[y][x + 1])
        if y > 0:
            adjacent_tiles.append(dungeon[y - 1][x])
        if y < height - 1:
            adjacent_tiles.append(dungeon[y + 1][x])

        return "#" in adjacent_tiles

    def mark_explored(self, x, y):
        # 指定されたマスを探索済みにする
        if 0 <= x < self.width and 0 <= y < self.height:
            self.explored[y][x] = True

    def mark_room_explored_by_id(self, room_id):
        # 指定されたIDの部屋を探索済みとしてマーク
        for y in range(self.height):
            for x in range(self.width):
                if self.room_info[y][x] == room_id:
                    self.mark_explored(x, y)

    def mark_adjacent_explored(self, x, y):
        # 隣接するマスを探索済みにする
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                self.mark_explored(x + dx, y + dy)

    def get_tile(self, x, y):
        # 座標がマップの範囲内にあるか確認
        if 0 <= x < len(self.tiles[0]) and 0 <= y < len(self.tiles):
            return self.tiles[y][x]
        return "#"  # 範囲外の場合は移動不可能を示す文字を返す

    def get_walkable_tiles(self):
        """return [(x,y),...]"""
        walkable_tiles = []
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                if tile == ".":  # '.' は移動可能な床を表す
                    walkable_tiles.append((x, y))
        return walkable_tiles

    def is_walkable(self, x, y):
        # 指定された座標がマップの範囲内かどうかを確認
        if 0 <= x < len(self.tiles[0]) and 0 <= y < len(self.tiles):
            # 指定された座標のタイルが移動可能かどうかを確認
            return self.tiles[y][x] in [".", "+", "#"]
        return False

    def get_room_of_cell(self, cell):
        # すべての部屋を調べ、指定したセルがその部屋に含まれているかを確認
        for room in self.rooms:
            if cell in room.cells:
                return room

        # 指定したセルがどの部屋にも含まれていない場合はNoneを返す
        return None

    def place_stair(self, stairs_x=0, stairs_y=0):
        self.stair = Stairs(stairs_x, stairs_y)
