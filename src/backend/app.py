from src.backend.ocrtranslate import OcrTranslationProcessor
from src.backend.common.plugin import PluginManager
from src.backend.common.event import EventSystem
from config import config


class WatchdOcrCore:
    def __init__(self):
        self._eventsys = None
        self._plugins_manager = None

    def load(self):
        self._register_event_system()
        self._register_plugins()
        self._register_processors()

    def _register_event_system(self):
        self._eventsys = EventSystem()

    def _register_plugins(self):
        self._plugins_manager = PluginManager(self._eventsys)
        self._plugins_manager.add_entry_point(config.PLUGINS_BACKEND_ENTRY_POINT)

    def _register_processors(self):
        self._ocr_translate_p = OcrTranslationProcessor(
            plugins=self._plugins_manager
        )


def app():
    core = WatchdOcrCore()
    core.load()


if __name__ == '__main__':
    app()
