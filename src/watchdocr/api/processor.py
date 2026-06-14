from src.common.api import KernelAPI
from src.watchdocr.processor.processor import PipelineStrategy


class ProcessorAPI(KernelAPI):
    def queue_pipeline(self, strategy: PipelineStrategy, context_data: dict):
        processor = self.kernel.objects.pull('watchdocr-processor')
        processor.queue_pipeline(strategy, context_data)

    def get_active(self) -> bool:
        processor = self.kernel.objects.pull('watchdocr-processor')
        return processor.get_active()
