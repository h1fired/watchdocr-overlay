

from . import WatchdOcrWorkflow
from src.watchdocr.processor.processor import PipelineStrategy
from src.common.utils.logging import log
from threading import Thread, Event
from config.preferences import settings


class LiveWorkflow(WatchdOcrWorkflow):
    def __init__(self, processor):
        super().__init__(processor)
        self._running = False
        self._th = None
        self._e = Event()

    def run(self):
        if self._running:
            return

        log.info('Starting LiveWorkflow thread...', extra={'title': 'Workflow'})
        self._e.clear()
        self._running = True
        self._th = Thread(target=self._run, daemon=True)
        self._th.start()

    def _run(self):
        while self._running:
            boundings = self._processor.context().boundings
            if not all(b == 0 for b in boundings):
                self._processor.queue_pipeline(
                    strategy=PipelineStrategy.OCR_TRANSLATION,
                    context_data={}
                )
                self._processor.wait_for_pipeline_finish()
            self._e.wait(settings.live_mode_recognition_frequency)
        log.info('LiveWorkflow thread exiting.', extra={'title': 'Workflow'})

    def close(self):
        if not self._running:
            return

        log.info('Stopping LiveWorkflow...', extra={'title': 'Workflow'})
        self._running = False
        self._e.set()
        if self._th and self._th.is_alive():
            self._th.join()
        log.info('LiveWorkflow stopped.', extra={'title': 'Workflow'})

    def execute(self):
        pass

    def is_active(self):
        return self._running
