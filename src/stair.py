from entity import Entity


class Stairs(Entity):
    def __init__(self, x=0, y=0):
        super().__init__(x, y, "<", "white")
