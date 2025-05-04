import os
import yaml
from typing import Any, Dict
from utils.constants import GameConstants

class ConfigLoader:
    """Handles loading of YAML configuration files."""
    
    def __init__(self, base_path: str = None):
        """
        Initialize the config loader.
        
        Args:
            base_path: Base path for configuration files. If None, uses parent of src2 directory.
        """
        if base_path is None:
            # Get the parent directory of src2
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.base_path = base_path
        
    def _build_path(self, *path_parts: str) -> str:
        """Build a full path from parts."""
        return os.path.join(self.base_path, *path_parts)
        
    def load_player_config(self) -> Dict[str, Any]:
        """Load player configuration from YAML."""
        path = self._build_path(GameConstants.get_player_config_path())
        return self.load_yaml(path)
        
    def load_enemy_config(self, enemy_name: str) -> Dict[str, Any]:
        """Load enemy configuration from YAML."""
        path = self._build_path(GameConstants.get_enemy_config_path(enemy_name))
        return self.load_yaml(path)
        
    def load_item_config(self, item_name: str) -> Dict[str, Any]:
        """Load item configuration from YAML."""
        path = self._build_path(GameConstants.get_item_config_path(item_name))
        return self.load_yaml(path)
        
    def load_yaml(self, path: str) -> Dict[str, Any]:
        """Load and parse a YAML file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file {path}: {str(e)}")
        except Exception as e:
            raise Exception(f"Error loading configuration file {path}: {str(e)}") 