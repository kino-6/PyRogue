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
    def __init__(self, heal_amount=const.HEALING_AMOUNT, duration=15):
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
    "full_restoration": FullRestorationEffect,  # 新しいエフェクトを追加
}
