

from . import WatchdOcrWorkflow
from src.watchdocr.processor.processor import PipelineStrategy
from src.common.utils.logging import log
from config.preferences import settings
import asyncio


class LiveWorkflow(WatchdOcrWorkflow):
    def __init__(self, processor):
        super().__init__(processor)
        self._task: asyncio.Task | None = None

    async def run(self):
        if self._task:
            return

        log.info('Starting LiveWorkflow task...', extra={'title': 'Workflow'})
        self._task = asyncio.create_task(self._run())

    async def _run(self):
        pipeline = None
        try:
            while True:
                boundings = self._processor.config().boundings
                if not all(b == 0 for b in boundings):
                    pipeline = self._processor.queue_pipeline(
                        strategy=PipelineStrategy.OCR_TRANSLATION,
                        context_data={}
                    )
                    if pipeline:
                        # Pipeline can be cancelled by a newer one, so wait
                        # for its finish without raising an exception
                        await asyncio.wait((pipeline,))
                        pipeline = None
                await asyncio.sleep(settings.live_mode_recognition_frequency)
        except asyncio.CancelledError:
            if pipeline:
                pipeline.cancel()
            raise
        finally:
            log.info('LiveWorkflow task exiting.', extra={'title': 'Workflow'})

    async def close(self):
        if not self._task:
            return

        log.info('Stopping LiveWorkflow...', extra={'title': 'Workflow'})
        task, self._task = self._task, None
        task.cancel()
        await asyncio.wait((task,))
        log.info('LiveWorkflow stopped.', extra={'title': 'Workflow'})

    def execute(self):
        pass

    def is_active(self):
        return self._task is not None
