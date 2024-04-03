import pytest
from unittest.mock import MagicMock
from ring import Ring
from effect import StrengthEffect  # effect.py から StrengthEffect をインポート

@pytest.fixture
def strength_effect():
    return StrengthEffect()

@pytest.fixture
def character_mock():
    character = MagicMock()
    character.damage_bonus = 0
    character.hit_bonus = 0
    return character

@pytest.fixture
def ring_with_strength_effect(strength_effect):
    ring_data = {"name": "Strength Ring", "use_effect": "add_strength"}
    ring = Ring(x=0, y=0, ring_data=ring_data, effect=strength_effect)
    return ring

@pytest.fixture
def no_effect_ring():
    # 効果がない指輪のインスタンスを作成
    ring_data = {"name": "Plain Ring", "use_effect": "no_effect"}
    return Ring(ring_data=ring_data)

@pytest.fixture
def invalid_effect_ring():
    # 存在しない効果を指定した指輪のインスタンスを作成
    ring_data = {"name": "Unknown Effect Ring", "use_effect": "invalid_effect"}
    return Ring(ring_data=ring_data)

def test_ring_with_strength_effect_equip(ring_with_strength_effect, character_mock):
    # Ringを装備する前のステータスを確認
    assert character_mock.damage_bonus == 0
    assert character_mock.hit_bonus == 0

    # Ringを装備
    ring_with_strength_effect.equip(character_mock)

    # 効果が適用されたことを確認
    assert character_mock.damage_bonus == 5
    assert character_mock.hit_bonus == 1

def test_ring_with_strength_effect_unequip(ring_with_strength_effect, character_mock):
    # まずRingを装備して効果を適用
    ring_with_strength_effect.equip(character_mock)

    # Ringを非装備
    ring_with_strength_effect.unequip(character_mock)

    # 効果が解除されたことを確認
    assert character_mock.damage_bonus == 0
    assert character_mock.hit_bonus == 0

def test_no_effect_ring_equip(no_effect_ring, character_mock):
    # Ringを装備
    no_effect_ring.equip(character_mock)
    # 何の効果も適用されないことを確認
    assert character_mock.damage_bonus == 0
    assert character_mock.hit_bonus == 0

def test_invalid_effect_ring_equip(invalid_effect_ring, character_mock):
    # 存在しない効果を指定したRingを装備
    invalid_effect_ring.equip(character_mock)
    # NoEffectが適用され、何の効果も適用されないことを確認
    assert character_mock.damage_bonus == 0
    assert character_mock.hit_bonus == 0
