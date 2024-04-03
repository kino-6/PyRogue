import pytest
from unittest.mock import patch, MagicMock
from armor import Armor, ArmorManager

@pytest.fixture
def armor_data():
    return {
        "name": "Test Armor",
        "char": "A",
        "color": "silver",
        "armor": 5,
        "throw_dice": "1d6",
        "protection_bonus": 2,
        "avoidance_bonus": 1,
        "use_effect": None
    }

@pytest.fixture
def armor_instance(armor_data):
    return Armor(armor_data=armor_data)

def test_armor_load_data(armor_instance, armor_data):
    for key, value in armor_data.items():
        assert getattr(armor_instance, key) == value

def test_armor_appraisal(armor_instance):
    armor_instance.appraisal()
    assert armor_instance.display_name.startswith("Test Armor 5")

@patch('armor.AssetsManager')
def test_get_random_armor(MockAssetsManager, armor_data):
    mock_assets_manager = MockAssetsManager.return_value
    mock_assets_manager.get_item_data_list.return_value = [armor_data]

    armor_manager = ArmorManager()
    random_armor = armor_manager.get_random_armor()

    assert random_armor.name == "Test Armor"
    assert random_armor.armor == 5
