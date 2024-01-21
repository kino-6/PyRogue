from character import Character
from weapon import Weapon
from enemy import Enemy
from game import Game
from weapon import Weapon
import random


class Fight:
    def __init__(self, player: Character, enemies: Character, game: Game, logger):
        self.player = player
        self.enemies = enemies
        self.game = game
        self.logger = logger

    def attack(self, attacker: Character, defender: Character, is_throw=False):
        # 攻撃の成功を判定
        did_hit, damage = self.roll_em(attacker, defender, is_throw=False)

        if did_hit:
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

    def roll_em(self, attacker: Character, defender: Character, is_throw=False):
        weapon = attacker.equipped_weapon
        base_dmg = attacker.status.strength
        attacker_level = attacker.status.exp_level
        def_armor = defender.status.armor

        # 武器とボーナスの設定
        if weapon is None:
            # 素手
            hit_bonus = 0
            dmg_bonus = 0
            attack_damage = "0d0"
        else:
            hit_bonus = weapon.hit_bonus
            dmg_bonus = weapon.dmg_bonus
            # ex. 1d3+1d3
            if is_throw:
                attack_damage = weapon.throw_dice
            else:
                attack_damage = weapon.wielded_dice

        # リングの効果（仮の処理）
        # ここにリングによる攻撃力やダメージのボーナスを適用するコードを追加

        # 防具やリングによる防御力のボーナスを適用するコードを追加

        # 攻撃処理
        did_hit = False
        damage = 0

        # ダメージ計算のループ
        for dmg in attack_damage.split("+"):
            ndice, nsides = map(int, dmg.split("d"))
            if self.swing(attacker_level, def_armor, hit_bonus):
                roll_result = self.roll_dice(ndice, nsides)

                max_damage = int(base_dmg / 2) + roll_result + dmg_bonus
                rnd_damage = int(max_damage / 16) + 1
                max_damage += random.randint(-rnd_damage, rnd_damage)

                damage = max(0, max_damage)
                did_hit = True

        return did_hit, damage

    def swing(self, attacker_level, defender_armor, hit_bonus):
        res = random.randint(1, 20)
        need = (20 - attacker_level) - defender_armor
        return res + hit_bonus >= need

    def roll_dice(self, ndice, nsides):
        # ndice: ダイスの数, nsides: ダイスの面の数
        return sum(random.randint(1, nsides) for _ in range(ndice))

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
        self.logger.info(f"{defender.status.name} is hit!")

    def handle_miss(self, attacker, defender):
        # 攻撃がミスした場合の処理
        self.logger.info(f"{attacker.status.name} missed {defender.status.name}!")
