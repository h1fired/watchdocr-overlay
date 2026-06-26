from pydantic import BaseModel, Field, ValidationError
from pathlib import Path
import yaml
from config import config
from dataclasses import dataclass


@dataclass
class SettingField:
    label: str
    description: str = ''
    modifiable: bool = True
    group: str = 'General'

    def as_dict(self) -> dict:
        return {
            'label': self.label,
            'description': self.description,
            'modifiable': self.modifiable,
            'group': self.group,
        }


class UserSettings(BaseModel):
    visual_hints_show: bool = Field(
        default=False,
        json_schema_extra=SettingField(
            label='Show visual hints',
            description='Display bounding-box hints on detected text regions.',
            group='Visual',
        ).as_dict(),
    )
    visual_hints_show_as_overlay: bool = Field(
        default=False,
        json_schema_extra=SettingField(
            label='Visual hints as overlay',
            description='Render hints as a transparent overlay instead of inline.',
            group='Visual',
        ).as_dict(),
    )
    screens_preview_enabled: bool = Field(
        default=False,
        json_schema_extra=SettingField(
            label='Screens preview',
            description='Show a live preview thumbnail of captured screen areas.',
            group='General',
        ).as_dict(),
    )
    source_language: str = Field(
        default='AUTO',
        json_schema_extra=SettingField(
            label='Source language',
            modifiable=False,
            group='Translation',
        ).as_dict(),
    )
    target_language: str = Field(
        default='ORIG',
        json_schema_extra=SettingField(
            label='Target language',
            modifiable=False,
            group='Translation',
        ).as_dict(),
    )

    model_config = {
        'validate_assignment': True,
        'strict': True
    }

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if not name.startswith('_'):
            self.save()

    def save(self, path: Path = config.USER_SETTINGS_PATH) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = self.model_dump()
        with open(path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, default_flow_style=False)

    @classmethod
    def load(cls, path: Path = config.USER_SETTINGS_PATH) -> 'UserSettings':
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

    @classmethod
    def modifiable_fields(cls) -> list[dict]:
        """
        Return metadata for all fields where modifiable=True, suitable for
        direct serialisation to QML as a QVariantList.

        Each dict has the shape:
            { key, label, description, group, type, value }
        where `type` is one of 'bool' | 'str' | 'int' | 'float'.
        """
        instance = settings  # use the live singleton so values are current
        result: list[dict] = []
        for field_name, field_info in cls.model_fields.items():
            extra = field_info.json_schema_extra or {}
            if not extra.get('modifiable', False):
                continue
            annotation = field_info.annotation
            if annotation is bool:
                field_type = 'bool'
            elif annotation is int:
                field_type = 'int'
            elif annotation is float:
                field_type = 'float'
            else:
                field_type = 'str'
            result.append({
                'key': field_name,
                'label': extra.get('label', field_name),
                'description': extra.get('description', ''),
                'group': extra.get('group', 'General'),
                'type': field_type,
                'value': getattr(instance, field_name),
            })
        return result


settings = UserSettings.load()
