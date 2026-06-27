

from . import WatchdOcrWorkflow
from src.watchdocr.processor.processor import PipelineStrategy
from threading import Thread, Event
from config import config


class LiveWorkflow(WatchdOcrWorkflow):
    def __init__(self, processor):
        super().__init__(processor)
        self._running = False
        self._th = None
        self._e = Event()

    def run(self):
        self._e.clear()
        self._running = True
        self._th = Thread(target=self._run, daemon=True)
        self._th.start()

    def _run(self):
        while self._running:
            if not all(b == 0 for b in self._processor.context().boundings):
                self._processor.queue_pipeline(
                    strategy=PipelineStrategy.OCR_TRANSLATION,
                    context_data={}
                )
                self._processor.wait_for_pipeline_finish()
            self._e.wait(config.LIVE_MANAGE_MODE_FREQ)

    def close(self):
        self._running = False
        self._e.set()
        if self._th and self._th.is_alive():
            self._th.join()
        self._processor.clean_current_pipelines()

    def execute(self):
        pass
