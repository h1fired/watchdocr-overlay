from frontend.viewmodels.common.mvvm import QmlViewModel
from qt.core import Property, Signal, Slot
from config import settings, settings_registry
from config.preferences import APP_OWNER, DEFAULT_GROUP
from pydantic import ValidationError
from typing import Any


class SettingsViewModel(QmlViewModel):
    _name = 'Settings'

    settingsChanged = Signal()
    restartPendingChanged = Signal()

    def onInit(self):
        self._sections: list[dict] | None = None
        self._restart_pending: list[str] = []
        settings_registry.listen(self._on_setting_changed)

    # App Settings only, kept flat for direct use across the UI
    @Property('QVariantMap', notify=settingsChanged)
    def values(self) -> dict:
        return settings.model_dump(mode='json')

    # Settings of every owner: {owner: {key: value}}
    @Property('QVariantMap', notify=settingsChanged)
    def ownerValues(self) -> dict:
        return {
            entry.owner: entry.model.model_dump(mode='json')
            for entry in settings_registry.entries()
        }

    @Property('QVariantList', constant=True)
    def sections(self) -> list:
        # Plugins register their Settings before UI is loaded
        if self._sections is None:
            self._sections = self._build_sections()
        return self._sections

    # Keys ('owner/key') changed in this session that apply after restart
    @Property('QVariantList', notify=restartPendingChanged)
    def restartPending(self) -> list:
        return self._restart_pending

    @Slot(str, 'QVariant')
    def set(self, key: str, value) -> None:
        self.setValue(APP_OWNER, key, value)

    @Slot(str, str, 'QVariant', result=str)
    def setValue(self, owner: str, key: str, value) -> str:
        """Returns error message, empty if value is applied."""
        try:
            settings_registry.set(owner, key, value)
        except ValidationError as e:
            return e.errors()[0]['msg']
        except KeyError as e:
            return str(e)
        return ''

    @Slot(str)
    def resetSection(self, section_id: str) -> None:
        section = next(
            (s for s in self.sections if s['id'] == section_id), None
        )
        if section is None:
            return
        settings_registry.reset(
            section['owner'],
            [field['key'] for field in section['fields']]
        )

    def _on_setting_changed(self, owner: str, key: str, value: Any):
        model = settings_registry.get(owner)
        if type(model).field_meta(key).requires_restart:
            pending_key = f'{owner}/{key}'
            if pending_key not in self._restart_pending:
                self._restart_pending = [*self._restart_pending, pending_key]
                self.restartPendingChanged.emit()

        self.settingsChanged.emit()

    def _build_sections(self) -> list[dict]:
        sections: list[dict] = []
        for entry in settings_registry.entries():
            fields = type(entry.model).describe_fields()
            if not fields:
                continue

            if entry.is_plugin:
                sections.append({
                    'id': entry.owner,
                    'title': entry.title,
                    'owner': entry.owner,
                    'plugin': True,
                    'fields': [
                        {**f, 'header': f['group'] or ''} for f in fields
                    ],
                })
                continue

            # App Settings are split into Sections by their group
            groups: dict[str, list[dict]] = {}
            for f in fields:
                group = f['group'] or DEFAULT_GROUP
                groups.setdefault(group, []).append({**f, 'header': ''})

            for group, group_fields in groups.items():
                sections.append({
                    'id': f'{entry.owner}.{group.lower()}',
                    'title': group,
                    'owner': entry.owner,
                    'plugin': False,
                    'fields': group_fields,
                })

        # App Sections always go before plugin ones
        sections.sort(key=lambda s: s['plugin'])
        return sections
