import utils.constants as const
from character import Character


class Player(Character):
    def __init__(self, x, y, status, logger):
        super().__init__(x, y, status, logger)
