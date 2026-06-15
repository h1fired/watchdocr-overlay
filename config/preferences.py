from pathlib import Path
from typing import Literal
import yaml
from pydantic import BaseModel, Field, ValidationError


CONFIG_PATH = Path('preferences.yaml')


class UserSettings(BaseModel):
    visual_hints_show: bool = False
    visual_hints_show_as_overlay: bool = False

    model_config = {
        'validate_assignment': True,
        'strict': True
    }

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if not name.startswith('_'):
            self.save()

    def save(self, path: Path = CONFIG_PATH) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = self.model_dump()
        with open(path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, default_flow_style=False)

    @classmethod
    def load(cls, path: Path = CONFIG_PATH) -> 'UserSettings':
        if not path.exists():
            # Automatically save defaults if no preferences file exists yet
            default_prefs = cls()
            default_prefs.save(path)
            return default_prefs
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            return cls.model_validate(data)
        except (ValidationError, Exception) as e:
            print(f'Warning: Failed to load config ({e}). Using defaults.')
            return cls()


settings = UserSettings.load()
