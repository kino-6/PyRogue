from game.character import Character, CharacterStatus

def build_player(config: dict, x: int, y: int) -> Character:
    status = CharacterStatus(
        name=config['name'],
        max_hp=config['max_hp'],
        attack=config['strength'],
        defense=config['armor'],
        gold=config['gold'],
        experience=config['exp'],
        level=config['level']
    )
    return Character(x, y, "player", config['char'], status) 