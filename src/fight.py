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

        # 武器情報の取得
        weapon_info = self._get_weapon_info(weapon, is_throw)
        
        # 攻撃処理
        did_hit = False
        total_damage = 0

        # ダメージ計算のループ
        for dmg in weapon_info['attack_damage'].split("+"):
            if self.swing(attacker_level, def_armor, weapon_info['hit_bonus']):
                ndice, nsides = map(int, dmg.split("d"))
                roll_result = self.roll_dice(ndice, nsides)
                damage = self._calculate_damage(
                    base_damage=base_dmg,
                    roll_result=roll_result,
                    weapon_bonus=weapon_info['dmg_bonus'],
                    attacker=attacker,
                    defender=defender
                )
                total_damage += damage
                did_hit = True

        return did_hit, total_damage

    def _get_weapon_info(self, weapon: Weapon, is_throw: bool) -> dict:
        """武器の情報を取得"""
        if weapon is None:
            return {
                'hit_bonus': 0,
                'dmg_bonus': 0,
                'attack_damage': '0d0'
            }
        return {
            'hit_bonus': weapon.hit_bonus,
            'dmg_bonus': weapon.dmg_bonus,
            'attack_damage': weapon.throw_dice if is_throw else weapon.wielded_dice
        }

    def _calculate_damage(self, base_damage: int, roll_result: int, 
                         weapon_bonus: int, attacker: Character, 
                         defender: Character) -> int:
        """ダメージ計算のロジック
        
        Parameters:
        -----------
        base_damage : int
            基本ダメージ（キャラクターの筋力など）
        roll_result : int
            ダイスロールの結果
        weapon_bonus : int
            武器のダメージボーナス
        attacker : Character
            攻撃者のキャラクター情報
        defender : Character
            防御者のキャラクター情報
        
        Returns:
        --------
        int
            最終的なダメージ値
        """
        # 基本ダメージ計算
        max_damage = int(base_damage / 2) + roll_result + weapon_bonus
        
        # ばらつきの追加
        rnd_damage = int(max_damage / 16) + 1
        max_damage += random.randint(-rnd_damage, rnd_damage)
        
        # 装備品による防御効果
        defense_modifier = self._calculate_equipment_modifier(attacker, defender)
        
        # 状態異常による補正
        status_modifier = self._calculate_status_modifier(attacker, defender)
        
        # 最終ダメージの計算（0未満にはならない）
        final_damage = max(0, max_damage + defense_modifier + status_modifier)
        
        print(f"Damage calculation: {final_damage} = {max_damage} (base) + {defense_modifier} (defense) + {status_modifier} (status)")
        
        return final_damage

    def _calculate_equipment_modifier(self, attacker: Character, defender: Character) -> int:
        """装備品による補正値の計算
        
        Parameters:
        -----------
        attacker : Character
            攻撃者のキャラクター情報
        defender : Character
            防御者のキャラクター情報
        
        Returns:
        --------
        int
            装備品による補正値（負の値になることが多い）
        """
        modifier = 0
        
        # 防具による軽減
        print(f"{defender.equipped_armor=}")
        if defender.equipped_armor:
            # 基本防具値
            modifier -= defender.equipped_armor.armor
            # 防具のprotection bonus
            if hasattr(defender.equipped_armor, 'protection_bonus'):
                modifier -= defender.equipped_armor.protection_bonus
        
            print(f"{modifier=}, {defender.equipped_armor.armor=}")

        # 指輪による防御補正
        if defender.equipped_left_ring and hasattr(defender.equipped_left_ring, 'protection_bonus'):
            modifier -= defender.equipped_left_ring.protection_bonus
        
        if defender.equipped_right_ring and hasattr(defender.equipped_right_ring, 'protection_bonus'):
            modifier -= defender.equipped_right_ring.protection_bonus
        
        print(f"Equipment defense modifier: {modifier} (armor + protection bonuses)")
        return modifier

    def _calculate_status_modifier(self, attacker: Character, defender: Character) -> int:
        """状態異常による補正値の計算"""
        # TODO: 状態異常の効果の実装
        return 0

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
        if isinstance(defender, Enemy):
            # 経験値の計算と付与
            exp_gain = defender.calculate_exp_reward()
            if self.player:
                self.player.gain_experience(exp_gain)
                self.logger.info(f"{defender.status.name} is killed! Gained {exp_gain} experience!")
            
            # 敵をenemiesリストから安全に削除
            if defender in self.enemies:
                self.enemies.remove(defender)
                self.game.remove_entity(defender)
        else:
            # プレイヤーの場合
            self.logger.info(f"{defender.status.name} is killed!")

    def handle_hit(self, defender: Character):
        # 攻撃がヒットしたが、敵が死亡しなかった場合の処理
        self.logger.info(f"{defender.status.name} is hit!")

    def handle_miss(self, attacker, defender):
        # 攻撃がミスした場合の処理
        self.logger.info(f"{attacker.status.name} missed {defender.status.name}!")
