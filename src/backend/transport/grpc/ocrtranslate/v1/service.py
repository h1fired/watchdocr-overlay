from . import ocrtranslate_pb2_grpc
from .ocrtranslate_pb2 import OcrTranslateRequest
from src.backend.core.grpc import GRPCService, UseDispatcher
from src.backend.ocrtranslate.processor import (
    OcrTranslationProcessor,
    OcrTranslationTask,
    ExecutionStrategy
)


class OcrTranslateService(
    GRPCService,
    ocrtranslate_pb2_grpc.OcrTranslateServiceServicer
):
    async def request_recognize(self, request: OcrTranslateRequest, context):
        await self._dispatcher.request_recognize(request)


class OcrTranslateDispatcher(UseDispatcher):
    def __init__(self, processor: OcrTranslationProcessor):
        super().__init__()
        self._processor = processor

    async def request_recognize(self, request: OcrTranslateRequest):
        task = OcrTranslationTask(
            strategy=ExecutionStrategy.ALL,
            context_data={
                'image_capture': {
                    'box': request.bounding
                }
            }
        )
        await self._processor.request(task)
