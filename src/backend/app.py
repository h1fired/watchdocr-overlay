from src.backend.ocrtranslate import OcrTranslationProcessor
from src.backend.common.plugin import PluginManager
from src.backend.common.event import EventSystem
from src.backend.transport.grpc import WatchdOcrGRPCServer
from config import config
import asyncio


class WatchdOcrCore:
    def __init__(self):
        self._eventsys = None
        self._plugins_manager = None
        self._grpc_server = None

    async def load(self):
        self._register_event_system()
        self._register_plugins()
        self._register_processors()
        await self._register_grpc_server()

    def _register_event_system(self):
        self._eventsys = EventSystem()

    def _register_plugins(self):
        self._plugins_manager = PluginManager(self._eventsys)
        self._plugins_manager.add_entry_point(config.PLUGINS_BACKEND_ENTRY_POINT)
        self._plugins_manager.init()

    def _register_processors(self):
        self._ocr_translate_p = OcrTranslationProcessor(
            plugins=self._plugins_manager
        )

    async def _register_grpc_server(self):
        self._grpc_server = WatchdOcrGRPCServer(config.GPRC_HOST)
        await self._grpc_server.run()
        await self._grpc_server.wait_for_termination()


def app():
    core = WatchdOcrCore()
    asyncio.run(core.load())


if __name__ == '__main__':
    app()
