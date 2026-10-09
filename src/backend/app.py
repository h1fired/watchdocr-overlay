from src.backend.ocrtranslate import OcrTranslationProcessor
from src.backend.common.plugin import PluginManager
from src.backend.common.event import EventSystem
from src.backend.transport.grpc import (
    WatchdOcrGRPCServer,
    OcrTranslateService,
    OcrTranslateDispatcher
)
from config import config
import asyncio
import argparse


class WatchdOcrBackend:
    def __init__(self):
        self._eventsys = None
        self._plugins_manager = None
        self._grpc_server = None

    async def load(self):
        self._register_event_system()
        self._register_plugins()
        await self._register_processors()

    def _register_event_system(self):
        self._eventsys = EventSystem()

    def _register_plugins(self):
        self._plugins_manager = PluginManager(self._eventsys)
        self._plugins_manager.add_entry_point(config.PLUGINS_BACKEND_ENTRY_POINT)
        self._plugins_manager.init()

    async def _register_processors(self):
        self._ocr_translate_p = OcrTranslationProcessor(
            plugins=self._plugins_manager
        )
        asyncio.create_task(self._ocr_translate_p.start())

    async def run(self, host: str, port: int):
        self._grpc_server = WatchdOcrGRPCServer(f'{host}:{port}')

        async def register_services():
            ocr_translate_d = OcrTranslateDispatcher(self._ocr_translate_p)
            ocr_translate_s = OcrTranslateService(ocr_translate_d)
            self._grpc_server.register_service(ocr_translate_s)

        await register_services()
        await self._grpc_server.run()


def app(host: str, port: int):
    core = WatchdOcrBackend()

    async def wait():
        await core.load()
        await core.run(host, port)
        try:
            await asyncio.Event().wait()
        finally:
            pass

    asyncio.run(wait())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host')
    parser.add_argument('--port', type=int)

    args = parser.parse_args()

    app(args.host, args.port)
