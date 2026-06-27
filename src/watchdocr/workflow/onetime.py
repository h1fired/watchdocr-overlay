from . import WatchdOcrWorkflow
from src.watchdocr.processor.processor import PipelineStrategy


class OnetimeWorkflow(WatchdOcrWorkflow):
    def run(self):
        pass

    def close(self):
        self._processor.clean_current_pipelines()

    def execute(self):
        self._processor.queue_pipeline(
            strategy=PipelineStrategy.OCR_TRANSLATION,
            context_data={}
        )
