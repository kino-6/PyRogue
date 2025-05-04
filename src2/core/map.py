from typing import List, Tuple, Set, Optional
import numpy as np

class Room:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    def center(self):
        return (self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2
    def intersect(self, other: 'Room') -> bool:
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

class GameMap:
    """Represents the game map and its state."""
    # Tile type constants
    TILE_WALL = 0
    TILE_FLOOR = 1
    TILE_DOOR = 2
    TILE_STAIRS = 3  # '<'
    TILE_ITEM = 4

    # Wall characters
    WALL_HORIZONTAL = '-'
    WALL_VERTICAL = '|'
    WALL_DOOR = '+'
    WALL_FLOOR = '.'
    WALL_PASSAGE = '#'
    WALL_STAIRS = '<'
    WALL_ITEM = '!'

    def __init__(self, width: int, height: int, rng: 'np.random.Generator' = None):
        self.width = width
        self.height = height
        self.rng = rng or np.random.default_rng()  # デフォルト生成器
        self.tiles = np.full((height, width), ' ', dtype='U1')  # Use Unicode string type
        self.explored = np.zeros((height, width), dtype=bool)
        self.room_info = np.full((height, width), -1, dtype=int)  # -1: no room
        self.rooms: List[Room] = []
        self.door_candidates: List[Tuple[int, int, str]] = []
        self.generate_dungeon()

    def generate_dungeon(self, num_rooms_range=(4, 12), room_size_range=(6, 12), max_attempts=30):
        while True:
            # Initialize dungeon with empty space
            self.tiles = np.full((self.height, self.width), ' ', dtype='U1')
            rooms = []
            room_id = 0

            # Generate outer walls
            self.tiles[0, :] = self.WALL_HORIZONTAL  # Top wall
            self.tiles[-1, :] = self.WALL_HORIZONTAL  # Bottom wall
            self.tiles[:, 0] = self.WALL_VERTICAL  # Left wall
            self.tiles[:, -1] = self.WALL_VERTICAL  # Right wall

            # Generate rooms
            for _ in range(max_attempts):
                if len(rooms) >= num_rooms_range[1]:
                    break

                w = self.rng.integers(room_size_range[0], room_size_range[1])
                h = self.rng.integers(room_size_range[0], room_size_range[1])
                x = self.rng.integers(1, self.width - w - 1)
                y = self.rng.integers(1, self.height - h - 1)

                new_room = {"x1": x, "y1": y, "x2": x + w, "y2": y + h}

                if not any(self.rooms_overlap(new_room, existing_room) for existing_room in rooms):
                    self.create_room(new_room)
                    rooms.append(new_room)

            if num_rooms_range[0] <= len(rooms) <= num_rooms_range[1]:
                break

        # Generate passages between rooms
        for i in range(1, len(rooms)):
            self.create_passage(rooms[i - 1], rooms[i])

        # Clean up rooms
        for room in rooms:
            self.cleanup_room(room)

        # Create doors
        for room in rooms:
            self.create_door(room)

        # Fix isolated doors
        self.fix_isolated_doors()

        # Record room IDs
        for room_id, room in enumerate(rooms):
            for y in range(room["y1"], room["y2"]):
                for x in range(room["x1"], room["x2"]):
                    self.room_info[y, x] = room_id

        # Place stairs in the last room
        if rooms:
            stair_x, stair_y = self.get_room_center(rooms[-1])
            self.tiles[stair_y, stair_x] = self.WALL_STAIRS
            self.player_start = self.get_room_center(rooms[0])

        # Mark explored tiles: all except the outermost wall (edges)
        self.mark_interior_explored()

    def rooms_overlap(self, room1, room2):
        return (
            room1["x1"] <= room2["x2"]
            and room1["x2"] >= room2["x1"]
            and room1["y1"] <= room2["y2"]
            and room1["y2"] >= room2["y1"]
        )

    def create_room(self, room):
        """Create a room on the map."""
        # Create horizontal walls
        for x in range(room["x1"], room["x2"]):
            self.tiles[room["y1"], x] = self.WALL_HORIZONTAL
            self.tiles[room["y2"] - 1, x] = self.WALL_HORIZONTAL

        # Create vertical walls
        for y in range(room["y1"] + 1, room["y2"] - 1):
            self.tiles[y, room["x1"]] = self.WALL_VERTICAL
            self.tiles[y, room["x2"] - 1] = self.WALL_VERTICAL

        # Create floor
        for y in range(room["y1"] + 1, room["y2"] - 1):
            for x in range(room["x1"] + 1, room["x2"] - 1):
                self.tiles[y, x] = self.WALL_FLOOR

        self.print_map()

    def get_room_center(self, room):
        return (
            (room["x1"] + room["x2"]) // 2,
            (room["y1"] + room["y2"]) // 2
        )

    def create_passage(self, room1, room2):
        # Get centers of both rooms
        center1 = self.get_room_center(room1)
        center2 = self.get_room_center(room2)

        # Create horizontal corridor
        for x in range(min(center1[0], center2[0]), max(center1[0], center2[0]) + 1):
            self.tiles[center1[1], x] = self.WALL_PASSAGE

        # Create vertical corridor
        for y in range(min(center1[1], center2[1]), max(center1[1], center2[1]) + 1):
            self.tiles[y, center2[0]] = self.WALL_PASSAGE

    def cleanup_room(self, room):
        # Clean up room interior
        for y in range(room["y1"] + 1, room["y2"] - 1):
            for x in range(room["x1"] + 1, room["x2"] - 1):
                self.tiles[y, x] = self.WALL_FLOOR

    def create_door(self, room):
        # Check horizontal walls
        for x in range(room["x1"], room["x2"]):
            if self.tiles[room["y1"], x] == self.WALL_PASSAGE:
                self.tiles[room["y1"], x] = self.WALL_DOOR
            if self.tiles[room["y2"] - 1, x] == self.WALL_PASSAGE:
                self.tiles[room["y2"] - 1, x] = self.WALL_DOOR

        # Check vertical walls
        for y in range(room["y1"], room["y2"]):
            if self.tiles[y, room["x1"]] == self.WALL_PASSAGE:
                self.tiles[y, room["x1"]] = self.WALL_DOOR
            if self.tiles[y, room["x2"] - 1] == self.WALL_PASSAGE:
                self.tiles[y, room["x2"] - 1] = self.WALL_DOOR

    def fix_isolated_doors(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y, x] == self.WALL_DOOR:
                    if not self.is_adjacent_to_passage(x, y):
                        self.tiles[y, x] = self.determine_wall_type(x, y)

    def determine_wall_type(self, x, y):
        # Check adjacent tiles to determine wall type
        if x > 0 and self.tiles[y, x - 1] in [' ', self.WALL_PASSAGE] and \
           x < self.width - 1 and self.tiles[y, x + 1] in [' ', self.WALL_PASSAGE]:
            return self.WALL_VERTICAL
        else:
            return self.WALL_HORIZONTAL

    def is_adjacent_to_passage(self, x, y):
        # Check adjacent tiles for passages
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if self.tiles[ny, nx] == self.WALL_PASSAGE:
                    return True
        return False

    def is_walkable(self, x: int, y: int) -> bool:
        """Check if a tile is walkable."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return self.tiles[y, x] in (self.WALL_FLOOR, self.WALL_DOOR, self.WALL_STAIRS, self.WALL_PASSAGE)
        
    def is_explored(self, x: int, y: int) -> bool:
        """Check if a tile has been explored."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return self.explored[y, x]
        
    def mark_explored(self, x: int, y: int) -> None:
        """Mark a tile as explored."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.explored[y, x] = True
            
    def get_room_id(self, x: int, y: int) -> Optional[int]:
        """Get the room ID at the given position."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None
        room_id = self.room_info[y, x]
        return room_id if room_id != -1 else None
        
    def mark_room_explored(self, room_id: int) -> None:
        """Mark all tiles in a room as explored."""
        for y in range(self.height):
            for x in range(self.width):
                if self.room_info[y, x] == room_id:
                    self.explored[y, x] = True
                    
    def get_walkable_tiles(self) -> List[Tuple[int, int]]:
        """Get a list of all walkable tile positions."""
        return [(x, y) for y in range(self.height) for x in range(self.width)
                if self.is_walkable(x, y)]
                
    def to_dict(self) -> dict:
        """Convert the map to a dictionary for serialization."""
        return {
            'width': self.width,
            'height': self.height,
            'tiles': self.tiles.tolist(),
            'explored': self.explored.tolist(),
            'room_info': self.room_info.tolist(),
            'rooms': [room for room in self.rooms]
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> 'GameMap':
        """Create a map from a dictionary."""
        game_map = cls(data['width'], data['height'])
        game_map.tiles = np.array(data['tiles'])
        game_map.explored = np.array(data['explored'])
        game_map.room_info = np.array(data['room_info'])
        game_map.rooms = data['rooms']
        return game_map

    def print_map(self):
        """Print the map for debugging purposes."""
        print("MAP VISUALIZATION:")
        for y in range(self.height):
            row = ''
            for x in range(self.width):
                row += self.tiles[y, x]
            print(row)

    def mark_interior_explored(self):
        """Mark all tiles except the outermost wall as explored."""
        self.explored[:, :] = False  # Reset all to unexplored
        self.explored[1:self.height-1, 1:self.width-1] = True 