import asyncio
from typing import Any


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
                await self.handle_item(item)
        except asyncio.CancelledError:
            pass
