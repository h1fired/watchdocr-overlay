from . import WatchdOcrWorkflow
from src.watchdocr.processor.processor import PipelineStrategy
from src.common.utils.logging import log


class OnetimeWorkflow(WatchdOcrWorkflow):
    def __init__(self, processor):
        super().__init__(processor)
        self._active = False

    def run(self):
        log.info('OnetimeWorkflow workflow active.', extra={'title': 'Workflow'})
        self._active = True

    def close(self):
        log.info('OnetimeWorkflow workflow closed.', extra={'title': 'Workflow'})
        self._active = False

    def is_active(self):
        return self._active

    def execute(self):
        if not self._active:
            raise RuntimeError('Cannot execute workflow while inactive')

        log.info(
            'OnetimeWorkflow execute triggered. Queueing OCR_TRANSLATION pipeline...',
            extra={'title': 'Workflow'}
        )
        self._processor.queue_pipeline(
            strategy=PipelineStrategy.OCR_TRANSLATION,
            context_data={}
        )
