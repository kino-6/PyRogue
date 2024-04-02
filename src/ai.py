class Node:
    """経路探索のためのノード"""

    def __init__(self, x, y, parent=None):
        self.x = x
        self.y = y
        self.parent = parent
        self.g = 0  # スタートからのコスト
        self.h = 0  # ゴールまでの推定コスト
        self.f = 0  # g + h


def heuristic(node, goal):
    """ヒューリスティック関数（ここではマンハッタン距離を使用）"""
    return abs(node.x - goal.x) + abs(node.y - goal.y)


def a_star_search(start, goal, game):
    """A*アルゴリズムによる経路探索"""
    open_set = [start]
    closed_set = set()

    while open_set:
        current_node = min(open_set, key=lambda node: node.f)
        if (current_node.x, current_node.y) == (goal.x, goal.y):
            path = []
            while current_node.parent:
                path.append(current_node)
                current_node = current_node.parent
            return path[::-1]  # ゴールからスタートへの経路を逆順にして返す

        open_set.remove(current_node)
        closed_set.add((current_node.x, current_node.y))

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
            neighbor = Node(current_node.x + dx, current_node.y + dy, current_node)
            if (neighbor.x, neighbor.y) in closed_set:
                continue
            if not game.is_walkable(neighbor.x, neighbor.y):
                continue

            neighbor.g = current_node.g + 1
            neighbor.h = heuristic(neighbor, goal)
            neighbor.f = neighbor.g + neighbor.h

            if any(node for node in open_set if (node.x, node.y) == (neighbor.x, neighbor.y) and node.g <= neighbor.g):
                continue

            open_set.append(neighbor)

    return None  # 経路が見つからない場合
