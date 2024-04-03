import pytest
from unittest.mock import MagicMock
from equipment import Equipment

@pytest.fixture
def sample_equipment():
    # Equipmentクラスのインスタンスを作成
    equipment = Equipment(name="Test Equipment", x=0, y=0, char="e", color="white", undefined_name="Unknown Equipment", is_cursed=False)
    return equipment

@pytest.fixture
def mock_character():
    # characterオブジェクトを模倣するMagicMockオブジェクトを作成
    character = MagicMock()
    character.equipped_left_ring = False  # equipped_left_ring属性を持つように設定
    return character

def test_equipment_initialization(sample_equipment):
    # Equipmentインスタンスの初期化をテスト
    assert sample_equipment.name == "Test Equipment"
    assert sample_equipment.is_equipped == False
    assert sample_equipment.is_cursed == False

def test_equipment_equip_unequip(sample_equipment, mock_character):
    # 装備と非装備の状態変更をテスト
    sample_equipment.equip(mock_character, None)  # mock_characterを使用
    assert sample_equipment.is_equipped == True

    sample_equipment.unequip(mock_character)  # mock_characterを使用
    assert sample_equipment.is_equipped == False

def test_equipment_curse_status(sample_equipment):
    # 呪いの状態をテスト
    assert sample_equipment.is_cursed == False  # 初期状態の確認

    # 呪い状態を変更してテスト
    sample_equipment.is_cursed = True
    assert sample_equipment.is_cursed == True
