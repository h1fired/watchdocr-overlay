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
    reset_on_reload: bool = False
    group: str = 'General'
    field_type: str | None = None

    def as_dict(self) -> dict:
        return {
            'label': self.label,
            'description': self.description,
            'modifiable': self.modifiable,
            'group': self.group,
            'field_type': self.field_type,
        }


class UserSettings(BaseModel):
    text_console_show: bool = Field(
        default=True,
        json_schema_extra=SettingField(
            label='Show text console',
            description='Display a text console for text interaction.',
            group='Visual',
        ).as_dict(),
    )
    visual_hints_show: bool = Field(
        default=True,
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
            description='Render hints even if overlay is hidden',
            group='Visual',
        ).as_dict(),
    )
    text_viewer_show: bool = Field(
        default=False,
        json_schema_extra=SettingField(
            reset_on_reload=True,
            label='Text viewer',
            description='Render interactive text viewer in non-overlay mode',
            group='Visual',
        ).as_dict(),
    )
    screens_preview_enabled: bool = Field(
        default=False,
        json_schema_extra=SettingField(
            label='Screens preview',
            modifiable=False,
            group='General'
        ).as_dict(),
    )
    live_mode_recognition_frequency: float = Field(
        default=1,
        json_schema_extra=SettingField(
            label='Live mode recognition frequency',
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
    overlay_toggle_hotkey: str = Field(
        default='Alt+B',
        json_schema_extra=SettingField(
            label='Overlay toggle hotkey',
            description='Trigger an overlay visibility.',
            group='Hotkeys',
            field_type='hotkey',
        ).as_dict(),
    )

    model_config = {
        'validate_assignment': True,
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

                for name in data.keys():
                    field = cls.model_fields.get(name)
                    if field.json_schema_extra.reset_on_reload:
                        data[name] = field.default

            return cls.model_validate(data)
        except (ValidationError, Exception) as e:
            print(f'Warning: Failed to load config ({e}). Using defaults.')
            return cls()

    @classmethod
    def modifiable_fields(cls) -> list[dict]:
        instance = settings  # use the live singleton so values are current
        result: list[dict] = []
        for field_name, field_info in cls.model_fields.items():
            extra = field_info.json_schema_extra or {}
            if not extra.get('modifiable', False):
                continue
            annotation = field_info.annotation
            if extra.get('field_type'):
                field_type = extra['field_type']
            elif annotation is bool:
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
