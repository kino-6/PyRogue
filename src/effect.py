import constants as const


class SpecialEffect:
    def apply_effect(self, character):
        pass

    def remove_effect(self, character):
        pass

    def on_turn(self, character):
        pass

    def on_attack(self, character, target):
        pass

class StrengthEffect(SpecialEffect):
    def apply_effect(self, character):
        character.damage_bonus += 5
        character.hit_bonus += 1
        character.status.strength += 3

    def remove_effect(self, character):
        character.damage_bonus -= 5
        character.hit_bonus -= 1
        character.status.strength -= 3

class NoEffect(SpecialEffect):
    def apply_effect(self, character):
        pass

    def remove_effect(self, character):
        pass

class AllHitEffect(SpecialEffect):
    def apply_effect(self, character):
        character.hit_bonus += 99  # 例
    def remove_effect(self, character):
        character.hit_bonus -= 99

class RegenerationEffect(SpecialEffect):
    def __init__(self, heal_amount=const.REGENERATION_HEAL_AMOUNT, duration=const.REGENERATION_DURATION):
        super().__init__()
        self.heal_amount = heal_amount
        self.duration = duration
        self.turns_passed = 0

    def apply_effect(self, character):
        """エフェクト付与時の処理"""
        super().apply_effect(character)
        character.add_effect(self)  # キャラクターにエフェクトを登録
        character.heal_damage(self.heal_amount)  # 即時回復を追加

    def remove_effect(self, character):
        """エフェクト解除時の処理"""
        super().remove_effect(character)
        character.remove_effect(self)  # キャラクターからエフェクトを削除

    def on_turn(self, character):
        """ターン毎の処理"""
        self.turns_passed += 1
        if self.turns_passed >= self.duration:
            self.remove_effect(character)
            character.add_logger("The regeneration effect wears off.")
        else:
            character.heal_damage(self.heal_amount)


class ShockWaveEffect(SpecialEffect):
    def on_attack(self, character, target):
        # 全体攻撃などの処理
        pass

class SeeInvisibleEffect(SpecialEffect):
    def apply_effect(self, character):
        character.can_see_invisible = True
    def remove_effect(self, character):
        character.can_see_invisible = False

class ProtectionEffect(SpecialEffect):
    def apply_effect(self, character):
        character.status.armor += 4
    def remove_effect(self, character):
        character.status.armor -= 4

class KeepHealthEffect(SpecialEffect):
    def on_take_damage(self, character, damage):
        # HPが0になるダメージを受けた時に1残すなど
        pass

class EnemySearchEffect(SpecialEffect):
    def apply_effect(self, character):
        character.enemy_search_active = True

    def remove_effect(self, character):
        character.enemy_search_active = False

class FullRestorationEffect(SpecialEffect):
    def apply_effect(self, character):
        """完全回復エフェクトを適用"""
        character.status.current_hp = character.status.max_hp
        # すべてのネガティブエフェクトを削除
        for effect in character.effects[:]:
            if isinstance(effect, (PoisonEffect, WeaknessEffect)):
                effect.remove_effect(character)
                character.effects.remove(effect)

    def remove_effect(self, character):
        """エフェクト解除時の処理（即時効果のため不要）"""
        pass

    def on_turn(self, character):
        """ターン毎の処理（即時効果のため不要）"""
        pass

class InvisibilityEffect(SpecialEffect):
    def __init__(self, duration=const.INVISIBILITY_DURATION):
        super().__init__()
        self.duration = duration
        self.turns_passed = 0

    def apply_effect(self, character):
        """透明化エフェクトを適用"""
        super().apply_effect(character)
        character.add_effect(self)
        character.is_invisible = True
        character.add_logger("You feel yourself becoming transparent!")

    def remove_effect(self, character):
        """エフェクト解除時の処理"""
        super().remove_effect(character)
        character.remove_effect(self)
        character.is_invisible = False
        character.add_logger("You feel yourself becoming visible again.")

    def on_turn(self, character):
        """ターン毎の処理"""
        self.turns_passed += 1
        if self.turns_passed >= self.duration:
            self.remove_effect(character)
        else:
            # 透明化中は敵から見つかりにくくなる
            character.evasion_bonus = 50  # 回避率を上昇

class PoisonEffect(SpecialEffect):
    def __init__(self, duration=const.POISON_DURATION):
        super().__init__()
        self.duration = duration
        self.turns_passed = 0

    def apply_effect(self, character):
        """毒エフェクトを適用"""
        super().apply_effect(character)
        character.add_effect(self)
        character.add_logger("You feel poisoned!")

    def remove_effect(self, character):
        """毒エフェクトを解除"""
        super().remove_effect(character)
        character.remove_effect(self)
        character.add_logger("The poison wears off.")

    def on_turn(self, character):
        """ターン毎の毒ダメージ"""
        self.turns_passed += 1
        if self.turns_passed >= self.duration:
            self.remove_effect(character)
        else:
            # 最大HPの1/16をダメージとして与える
            damage = max(1, character.status.max_hp // const.POISON_DAMAGE_DIVISOR)
            character.take_damage(damage)
            character.add_logger(f"The poison hurts! You take {damage} damage. ({self.turns_passed}/{self.duration} turns)")

class WeaknessEffect(SpecialEffect):
    def __init__(self, duration=3):
        super().__init__()
        self.duration = duration
        self.turns_passed = 0
        self.strength_reduction = 2

    def apply_effect(self, character):
        """弱体化エフェクトを適用"""
        super().apply_effect(character)
        character.add_effect(self)
        character.status.strength -= self.strength_reduction
        character.add_logger("You feel weakened!")

    def remove_effect(self, character):
        """弱体化エフェクトを解除"""
        super().remove_effect(character)
        character.remove_effect(self)
        character.status.strength += self.strength_reduction
        character.add_logger("You feel your strength returning.")

    def on_turn(self, character):
        """ターン毎の処理"""
        self.turns_passed += 1
        if self.turns_passed >= self.duration:
            self.remove_effect(character)

class SleepEffect(SpecialEffect):
    def __init__(self, duration=const.SLEEP_DURATION):
        super().__init__()
        self.duration = duration
        self.turns_passed = 0

    def apply_effect(self, character):
        """睡眠エフェクトを適用"""
        # 既に睡眠状態の場合は適用しない
        if not character.can_act:
            return
            
        super().apply_effect(character)
        character.add_effect(self)
        character.add_logger("You feel drowsy...")
        character.can_act = False  # 行動不能状態にする

    def remove_effect(self, character):
        """睡眠エフェクトを解除"""
        super().remove_effect(character)
        character.remove_effect(self)
        character.can_act = True  # 行動可能状態に戻す
        character.add_logger("You wake up!")

    def on_turn(self, character):
        """ターン毎の処理"""
        self.turns_passed += 1
        if self.turns_passed >= self.duration:
            self.remove_effect(character)
        else:
            character.add_logger(f"You are asleep... ({self.turns_passed}/{self.duration} turns)")

EFFECT_MAP = {
    "no_effect": NoEffect,
    "add_strength": StrengthEffect,
    "all_hit": AllHitEffect,
    "regeneration": RegenerationEffect,
    "shock_wave": ShockWaveEffect,
    "see_invisible": SeeInvisibleEffect,
    "protection": ProtectionEffect,
    "keep_health": KeepHealthEffect,
    "enemy_search": EnemySearchEffect,
    "full_restoration": FullRestorationEffect,
    "invisibility": InvisibilityEffect,
    "poison": PoisonEffect,
    "sleep": SleepEffect
}
