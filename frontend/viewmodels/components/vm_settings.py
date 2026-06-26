from frontend.viewmodels.common.mvvm import QmlViewModel
from qt.core import Property, Signal, Slot
from config import settings
from config.preferences import UserSettings


class SettingsViewModel(QmlViewModel):
    _name = 'Settings'

    settingsChanged = Signal()

    @Property('QVariantMap', notify=settingsChanged)
    def values(self) -> dict:
        return settings.model_dump()

    @Property('QVariantList', notify=settingsChanged)
    def fields(self) -> list:
        return UserSettings.modifiable_fields()

    @Slot(str, 'QVariant')
    def set(self, key: str, value) -> None:
        if hasattr(settings, key):
            setattr(settings, key, value)
            self.settingsChanged.emit()

    @Slot()
    def refresh(self) -> None:
        self.settingsChanged.emit()
