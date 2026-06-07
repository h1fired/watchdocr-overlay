from src.common.api import KernelAPI
from src.watchdocr.processor import ProcessorCommandType


class ProcessorAPI(KernelAPI):
    def queue_command(self, command: ProcessorCommandType, *args):
        processor = self.kernel.objects.pull('watchdocr-processor')
        processor.queue_command(command, *args)

    def get_active(self) -> bool:
        processor = self.kernel.objects.pull('watchdocr-processor')
        return processor.recognizer().is_active()
