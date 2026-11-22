from __future__ import annotations
from pydantic import BaseModel, Field, PrivateAttr, ValidationError
from pathlib import Path
from dataclasses import dataclass, asdict
from contextlib import contextmanager, suppress
from typing import Any, Callable, Literal, TypeVar, get_args, get_origin
import os
import tempfile
import yaml
from config import config
from src.common.utils.logging import log


LOG_TITLE = 'Settings'

APP_OWNER = 'app'
PLUGINS_KEY = 'plugins'
DEFAULT_GROUP = 'General'

SettingType = Literal[
    'bool', 'choice', 'number', 'text', 'secret', 'hotkey'
]


@dataclass
class SettingField:
    label: str
    description: str = ''
    modifiable: bool = True
    runtime_only: bool = False
    # App settings: Settings Section title. Plugin settings: header inside
    # the plugin's Settings Section
    group: str | None = None
    field_type: SettingType | None = None  # Inferred from annotation if None
    options: dict[str, str] | None = None  # Value -> label, for 'choice' fields
    step: float | None = None  # For 'number' fields
    enabled_if: str | None = None  # Bool setting of the same model
    requires_restart: bool = False

    def as_dict(self) -> dict:
        return asdict(self)


class SettingsModel(BaseModel):
    """Base for every set of Settings, both app's and plugin's."""

    model_config = {
        'validate_assignment': True,
    }

    _listener: Callable[[str, Any], None] | None = PrivateAttr(default=None)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if not name.startswith('_') and self._listener is not None:
            self._listener(name, value)

    @classmethod
    def field_meta(cls, name: str) -> SettingField:
        extra = cls.model_fields[name].json_schema_extra or {}
        return SettingField(**{'label': name, **extra})

    @classmethod
    def from_data(cls, data: Any) -> SettingsModel:
        """Builds model from stored data, falling back to defaults only
        for the values that are unknown or invalid."""
        if not isinstance(data, dict):
            data = {}

        values = {
            name: value for name, value in data.items()
            if name in cls.model_fields
            and not cls.field_meta(name).runtime_only
        }

        while True:
            try:
                return cls.model_validate(values)
            except ValidationError as e:
                invalid = {err['loc'][0] for err in e.errors() if err['loc']}
                invalid &= values.keys()
                if not invalid:
                    log.warning(
                        'Failed to load %s (%s). Using defaults.',
                        cls.__name__, e,
                        extra={'title': LOG_TITLE}
                    )
                    return cls()

                log.warning(
                    'Invalid stored values in %s, using defaults for: %s',
                    cls.__name__, ', '.join(sorted(invalid)),
                    extra={'title': LOG_TITLE}
                )
                for name in invalid:
                    values.pop(name)

    def to_data(self) -> dict:
        data = self.model_dump(mode='json')
        return {
            name: value for name, value in data.items()
            if not self.field_meta(name).runtime_only
        }

    @classmethod
    def describe_fields(cls) -> list[dict]:
        """Describes Settings shown in the Settings window."""
        result: list[dict] = []
        for name, field_info in cls.model_fields.items():
            meta = cls.field_meta(name)
            if not meta.modifiable:
                continue

            annotation = field_info.annotation
            field_type = meta.field_type or _infer_field_type(annotation)

            options = meta.options
            if field_type == 'choice' and options is None:
                options = {str(v): str(v) for v in get_args(annotation)}

            minimum, maximum = _field_bounds(field_info)
            integer = annotation is int
            step = meta.step if meta.step is not None else (1 if integer else 0.1)

            result.append({
                'key': name,
                'label': meta.label,
                'description': meta.description,
                'group': meta.group,
                'type': field_type,
                'options': options,
                'min': minimum,
                'max': maximum,
                'step': step,
                'integer': integer,
                'enabled_if': meta.enabled_if,
                'requires_restart': meta.requires_restart,
            })
        return result


def _infer_field_type(annotation: Any) -> SettingType:
    if annotation is bool:
        return 'bool'
    elif annotation in (int, float):
        return 'number'
    elif get_origin(annotation) is Literal:
        return 'choice'
    return 'text'


def _field_bounds(field_info) -> tuple[float | None, float | None]:
    minimum = maximum = None
    for constraint in field_info.metadata:
        for attr in ('ge', 'gt'):
            if getattr(constraint, attr, None) is not None:
                minimum = getattr(constraint, attr)
        for attr in ('le', 'lt'):
            if getattr(constraint, attr, None) is not None:
                maximum = getattr(constraint, attr)
    return minimum, maximum


M = TypeVar('M', bound=SettingsModel)


@dataclass(slots=True)
class SettingsEntry:
    owner: str  # 'app' or plugin id
    title: str
    is_plugin: bool
    model: SettingsModel
    callback: Callable[[str, Any], None] | None = None

    @property
    def storage_path(self) -> tuple[str, ...]:
        if self.is_plugin:
            return (PLUGINS_KEY, self.owner)
        return (self.owner,)


class SettingsRegistry:
    """Keeps every registered set of Settings and stores them in one file.

    Stored data of sets which are not registered right now (e.g. plugin
    is missing) is kept untouched.
    """

    def __init__(self, path: Path):
        self._path = path
        self._data = self._read()
        self._entries: dict[str, SettingsEntry] = {}
        self._listeners: list[Callable[[str, str, Any], None]] = []
        self._batch_depth = 0
        self._save_pending = False

    def register_app(self, model_cls: type[M]) -> M:
        return self._register(APP_OWNER, 'App', False, model_cls)

    def register_plugin(
        self,
        plugin_id: str,
        title: str,
        model_cls: type[M],
        callback: Callable[[str, Any], None] | None = None
    ) -> M:
        return self._register(plugin_id, title, True, model_cls, callback)

    def entries(self) -> tuple[SettingsEntry, ...]:
        return tuple(self._entries.values())

    def get(self, owner: str) -> SettingsModel:
        return self._entries[owner].model

    def set(self, owner: str, name: str, value: Any):
        """Raises KeyError for unknown setting, ValidationError for invalid value."""
        model = self.get(owner)
        if name not in type(model).model_fields:
            raise KeyError(f'Unknown setting {owner}.{name}')
        setattr(model, name, value)

    def reset(self, owner: str, names: list[str]):
        model = self.get(owner)
        fields = type(model).model_fields
        with self.batch():
            for name in names:
                setattr(model, name, fields[name].get_default(call_default_factory=True))

    def listen(self, callback: Callable[[str, str, Any], None]):
        self._listeners.append(callback)

    @contextmanager
    def batch(self):
        """Saves file once after all changes made inside."""
        self._batch_depth += 1
        try:
            yield
        finally:
            self._batch_depth -= 1
            if not self._batch_depth and self._save_pending:
                self.save()

    def save(self):
        if self._batch_depth:
            self._save_pending = True
            return
        self._save_pending = False

        data = dict(self._data)
        for entry in self._entries.values():
            *parents, key = entry.storage_path
            node = data
            for parent in parents:
                child = node.get(parent)
                node[parent] = dict(child) if isinstance(child, dict) else {}
                node = node[parent]
            node[key] = entry.model.to_data()
        self._data = data

        try:
            _write_yaml_atomic(self._path, data)
        except Exception:
            log.exception(
                'Failed to save settings to %s', self._path,
                extra={'title': LOG_TITLE}
            )

    def _register(
        self,
        owner: str,
        title: str,
        is_plugin: bool,
        model_cls: type[M],
        callback: Callable[[str, Any], None] | None = None
    ) -> M:
        if owner in self._entries:
            raise ValueError(f'Settings of {owner} are already registered')

        entry = SettingsEntry(owner, title, is_plugin, None, callback)
        node = self._data
        for key in entry.storage_path:
            node = node.get(key) if isinstance(node, dict) else None

        model = model_cls.from_data(node)
        model._listener = lambda name, value: self._on_changed(entry, name, value)
        entry.model = model
        self._entries[owner] = entry
        return model

    def _on_changed(self, entry: SettingsEntry, name: str, value: Any):
        self.save()

        if entry.callback is not None:
            try:
                entry.callback(name, value)
            except Exception:
                log.exception(
                    'Settings change callback of %s failed', entry.owner,
                    extra={'title': LOG_TITLE}
                )

        for listener in self._listeners:
            listener(entry.owner, name, value)

    def _read(self) -> dict:
        if not self._path.exists():
            return {}

        try:
            with open(self._path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except (OSError, yaml.YAMLError):
            log.exception(
                'Failed to read settings from %s. Using defaults.', self._path,
                extra={'title': LOG_TITLE}
            )
            self._backup_unreadable()
            return {}

        if data is None:
            return {}
        elif not isinstance(data, dict):
            log.warning(
                'Settings file %s has wrong format. Using defaults.', self._path,
                extra={'title': LOG_TITLE}
            )
            self._backup_unreadable()
            return {}

        # Anything else (e.g. old flat format) is dropped on the next save
        return {
            key: value for key, value in data.items()
            if key in (APP_OWNER, PLUGINS_KEY)
        }

    def _backup_unreadable(self):
        # Keep broken file so it's not silently lost on the next save
        with suppress(OSError):
            os.replace(self._path, self._path.with_name(self._path.name + '.bak'))


def _write_yaml_atomic(path: Path, data: dict):
    # File is written next to the target and swapped in at once,
    # so interrupted write never leaves half of the file
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        dir=path.parent,
        prefix=f'.{path.name}.',
        suffix='.tmp'
    )
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            yaml.safe_dump(
                data, f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except BaseException:
        with suppress(OSError):
            os.remove(tmp_path)
        raise


class UserSettings(SettingsModel):
    live_mode_recognition_frequency: float = Field(
        default=1,
        ge=0.05,
        le=60,
        json_schema_extra=SettingField(
            label='Live mode recognition frequency',
            description='Seconds between recognitions in live mode.',
            group='General',
            step=0.05,
        ).as_dict(),
    )
    ocr_recognition_scale: Literal['adaptive', 'original'] = Field(
        default='adaptive',
        json_schema_extra=SettingField(
            label='Recognition scale',
            description='Shrink image by previous text size for faster recognition.',
            group='General',
            options={
                'adaptive': 'Adaptive',
                'original': 'Original',
            },
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
    visual_hints_style: Literal['simple_inpaint', 'solid'] = Field(
        default='simple_inpaint',
        json_schema_extra=SettingField(
            label='Visual hints style',
            description='Solid is faster, Simple inpaint keeps original look.',
            group='Visual',
            options={
                'simple_inpaint': 'Simple inpaint',
                'solid': 'Solid',
            },
        ).as_dict(),
    )
    text_viewer_show: bool = Field(
        default=False,
        json_schema_extra=SettingField(
            runtime_only=True,
            label='Text viewer',
            description='Render interactive text viewer in non-overlay mode',
            group='Visual',
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


settings_registry = SettingsRegistry(config.USER_SETTINGS_PATH)
settings = settings_registry.register_app(UserSettings)
