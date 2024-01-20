from character import Character
from enemy import Enemy
from game import Game


class Fight:
    def __init__(self, player: Character, enemies: Character, game: Game, logger):
        self.player = player
        self.enemies = enemies
        self.game = game
        self.logger = logger

    def attack(self, attacker: Character, defender: Character):
        # 攻撃の成功を判定
        hit = self.calculate_hit_chance(attacker, defender)

        if hit:
            damage = self.calculate_damage(attacker, defender)
            is_killed = defender.take_damage(damage)
            self.logger.info(f"{attacker.status.name} attacks {defender.status.name} for {damage} damage.")

            if is_killed:
                self.handle_death(defender)
            else:
                self.handle_hit(defender)

            return True
        else:
            self.handle_miss(attacker, defender)
            return False

    def calculate_hit_chance(self, attacker: Character, defender: Character):
        # 基本命中率: 攻撃者の攻撃力と防御者の防御力を考慮
        base_hit_chance = attacker.status.based_hit_rate

        # その他の修正: 例えば、特定のアイテムや状態効果による修正
        # modifiers = get_hit_chance_modifiers(attacker, defender)
        modifiers = 0

        # 最終的な命中率を計算
        final_hit_chance = base_hit_chance + modifiers

        # 命中率は0から100の範囲に収める
        final_hit_chance = max(0, min(final_hit_chance, 100))

        return final_hit_chance

    def calculate_damage(self, attacker: Character, defender: Character):
        # ダメージ計算ロジック
        return attacker.status.attack_power - defender.status.armor

    def handle_death(self, defender: Character):
        # 敵が死亡した場合の処理
        self.logger.info(f"{defender.status.name} is killed!")
        if isinstance(defender, Enemy):
            # 敵をenemiesリストから安全に削除
            if defender in self.enemies:
                self.enemies.remove(defender)
                self.game.remove_entity(defender)

    def handle_hit(self, defender: Character):
        # 攻撃がヒットしたが、敵が死亡しなかった場合の処理
        print(f"{defender.status.name} is hit!")

    def handle_miss(self, attacker, defender):
        # 攻撃がミスした場合の処理
        print(f"{attacker.status.name} missed {defender.status.name}!")
