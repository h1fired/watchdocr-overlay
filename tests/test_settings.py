from config.preferences import (
    SettingsModel,
    SettingsRegistry,
    SettingField,
    UserSettings
)
from config import preferences
from pydantic import Field, ValidationError
from typing import Literal
import pytest
import yaml


class SampleSettings(SettingsModel):
    enabled: bool = Field(
        default=True,
        json_schema_extra=SettingField(label='Enabled').as_dict(),
    )
    style: Literal['a', 'b'] = Field(
        default='a',
        json_schema_extra=SettingField(label='Style').as_dict(),
    )
    interval: float = Field(
        default=1.0,
        ge=0.5,
        le=10,
        json_schema_extra=SettingField(label='Interval', step=0.5).as_dict(),
    )
    api_key: str = Field(
        default='',
        json_schema_extra=SettingField(
            label='API key',
            field_type='secret',
            enabled_if='enabled',
            requires_restart=True,
        ).as_dict(),
    )
    session_flag: bool = Field(
        default=False,
        json_schema_extra=SettingField(
            label='Session flag',
            runtime_only=True,
        ).as_dict(),
    )
    hidden_state: str = Field(
        default='x',
        json_schema_extra=SettingField(
            label='Hidden',
            modifiable=False,
        ).as_dict(),
    )


def write_yaml(path, data):
    path.write_text(yaml.safe_dump(data), encoding='utf-8')


def read_yaml(path):
    return yaml.safe_load(path.read_text(encoding='utf-8'))


def test_missing_file_gives_defaults_without_writing(tmp_path):
    path = tmp_path / 'settings.yaml'
    registry = SettingsRegistry(path)

    settings = registry.register_app(SampleSettings)

    assert settings.model_dump() == SampleSettings().model_dump()
    assert not path.exists()


def test_unknown_keys_do_not_reset_known_values(tmp_path):
    path = tmp_path / 'settings.yaml'
    write_yaml(path, {'app': {'enabled': False, 'removed_setting': 1}})

    settings = SettingsRegistry(path).register_app(SampleSettings)

    assert settings.enabled is False


def test_invalid_value_falls_back_only_for_that_setting(tmp_path):
    path = tmp_path / 'settings.yaml'
    write_yaml(path, {
        'app': {'enabled': False, 'style': 'removed', 'interval': 99}
    })

    settings = SettingsRegistry(path).register_app(SampleSettings)

    assert settings.enabled is False
    assert settings.style == 'a'
    assert settings.interval == 1.0


def test_runtime_only_setting_is_neither_loaded_nor_saved(tmp_path):
    path = tmp_path / 'settings.yaml'
    write_yaml(path, {'app': {'session_flag': True}})
    registry = SettingsRegistry(path)
    settings = registry.register_app(SampleSettings)

    assert settings.session_flag is False

    settings.session_flag = True
    assert 'session_flag' not in read_yaml(path)['app']


def test_change_is_saved_and_loaded_back(tmp_path):
    path = tmp_path / 'settings.yaml'
    settings = SettingsRegistry(path).register_app(SampleSettings)

    settings.style = 'b'

    reloaded = SettingsRegistry(path).register_app(SampleSettings)
    assert reloaded.style == 'b'


def test_invalid_assignment_raises_and_keeps_value(tmp_path):
    registry = SettingsRegistry(tmp_path / 'settings.yaml')
    registry.register_app(SampleSettings)

    with pytest.raises(ValidationError):
        registry.set('app', 'interval', 100)

    assert registry.get('app').interval == 1.0


def test_unknown_setting_raises_key_error(tmp_path):
    registry = SettingsRegistry(tmp_path / 'settings.yaml')
    registry.register_app(SampleSettings)

    with pytest.raises(KeyError):
        registry.set('app', 'nope', 1)


def test_plugin_settings_are_stored_under_plugin_id(tmp_path):
    path = tmp_path / 'settings.yaml'
    registry = SettingsRegistry(path)
    registry.register_app(SampleSettings)
    plugin_settings = registry.register_plugin(
        'sample-plugin', 'Sample', SampleSettings
    )

    plugin_settings.style = 'b'

    data = read_yaml(path)
    assert data['plugins']['sample-plugin']['style'] == 'b'
    assert data['app']['style'] == 'a'


def test_settings_of_missing_plugin_are_kept(tmp_path):
    path = tmp_path / 'settings.yaml'
    write_yaml(path, {'plugins': {'missing-plugin': {'style': 'b'}}})
    registry = SettingsRegistry(path)
    settings = registry.register_app(SampleSettings)

    settings.enabled = False

    assert read_yaml(path)['plugins']['missing-plugin'] == {'style': 'b'}


def test_plugin_callback_and_listeners_get_changes(tmp_path):
    registry = SettingsRegistry(tmp_path / 'settings.yaml')
    plugin_changes, all_changes = [], []
    registry.listen(lambda *args: all_changes.append(args))
    settings = registry.register_plugin(
        'sample-plugin', 'Sample', SampleSettings,
        lambda name, value: plugin_changes.append((name, value))
    )

    settings.style = 'b'

    assert plugin_changes == [('style', 'b')]
    assert all_changes == [('sample-plugin', 'style', 'b')]


def test_failing_plugin_callback_does_not_break_saving(tmp_path):
    path = tmp_path / 'settings.yaml'
    registry = SettingsRegistry(path)

    def callback(name, value):
        raise RuntimeError('boom')

    settings = registry.register_plugin(
        'sample-plugin', 'Sample', SampleSettings, callback
    )
    settings.style = 'b'

    assert read_yaml(path)['plugins']['sample-plugin']['style'] == 'b'


def test_reset_restores_defaults_with_single_save(tmp_path, monkeypatch):
    path = tmp_path / 'settings.yaml'
    write_yaml(path, {'app': {'enabled': False, 'style': 'b'}})
    registry = SettingsRegistry(path)
    settings = registry.register_app(SampleSettings)

    writes = []
    original_write = preferences._write_yaml_atomic

    def counting_write(*args):
        writes.append(1)
        original_write(*args)

    monkeypatch.setattr(preferences, '_write_yaml_atomic', counting_write)

    registry.reset('app', ['enabled', 'style'])

    assert settings.enabled is True and settings.style == 'a'
    assert read_yaml(path)['app']['style'] == 'a'
    assert len(writes) == 1


def test_unreadable_file_is_backed_up(tmp_path):
    path = tmp_path / 'settings.yaml'
    path.write_text('app: [unclosed', encoding='utf-8')

    settings = SettingsRegistry(path).register_app(SampleSettings)

    assert settings.model_dump() == SampleSettings().model_dump()
    assert (tmp_path / 'settings.yaml.bak').exists()


def test_failed_write_keeps_previous_file(tmp_path, monkeypatch):
    path = tmp_path / 'settings.yaml'
    write_yaml(path, {'app': {'style': 'b'}})
    registry = SettingsRegistry(path)
    settings = registry.register_app(SampleSettings)

    def broken_dump(*args, **kwargs):
        raise RuntimeError('disk full')

    monkeypatch.setattr(yaml, 'safe_dump', broken_dump)
    settings.enabled = False

    assert read_yaml(path) == {'app': {'style': 'b'}}
    assert list(tmp_path.iterdir()) == [path]


def test_describe_fields():
    fields = {f['key']: f for f in SampleSettings.describe_fields()}

    assert 'hidden_state' not in fields
    assert fields['enabled']['type'] == 'bool'
    assert fields['style']['type'] == 'choice'
    assert fields['style']['options'] == {'a': 'a', 'b': 'b'}
    assert fields['interval']['type'] == 'number'
    assert (fields['interval']['min'], fields['interval']['max']) == (0.5, 10)
    assert fields['interval']['step'] == 0.5
    assert fields['api_key']['type'] == 'secret'
    assert fields['api_key']['enabled_if'] == 'enabled'
    assert fields['api_key']['requires_restart'] is True


def test_user_settings_keep_existing_flat_file_values_out(tmp_path):
    # Old flat format is not migrated, app starts with defaults
    path = tmp_path / 'settings.yaml'
    write_yaml(path, {'text_console_show': False})

    settings = SettingsRegistry(path).register_app(UserSettings)

    assert settings.text_console_show is True
