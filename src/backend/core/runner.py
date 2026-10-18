import asyncio
from typing import Any
from src.backend.common.utils.logging import log


LOG_TITLE = 'RUNNER'


class Runner:
    def __init__(self):
        self._q = asyncio.Queue()
        self._running = False
        self._task = None

    async def start(self):
        if self._task and not self._task.done():
            return
        self._running = True
        await self._run()

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            await self._task
            for _ in range(self._q.qsize()):
                self._q.get_nowait()

    async def put(self, item: Any):
        await self._q.put(item)

    async def handle_item(self, item: Any):
        raise NotImplementedError

    async def _run(self):
        try:
            while self._running:
                item = await self._q.get()
                try:
                    await self.handle_item(item)
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    log.exception(
                        "Error while handling item %s",
                        str(e),
                        extra={'title': LOG_TITLE}
                    )
        except asyncio.CancelledError:
            pass
