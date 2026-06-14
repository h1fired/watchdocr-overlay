from src.common.api import KernelAPI
from src.watchdocr.processor2.processor import PipelineStrategy


class ProcessorAPI(KernelAPI):
    def queue_pipeline(self, strategy: PipelineStrategy, context_data: dict):
        processor = self.kernel.objects.pull('watchdocr-processor2')
        processor.queue_pipeline(strategy, context_data)

    def get_active(self) -> bool:
        processor = self.kernel.objects.pull('watchdocr-processor2')
        return processor.get_active()
