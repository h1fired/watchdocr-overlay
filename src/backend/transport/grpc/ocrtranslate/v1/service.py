from . import ocrtranslate_pb2_grpc
from .ocrtranslate_pb2 import OcrTranslateRequest, OcrTranslateResult
from src.backend.core.grpc import GRPCService, UseDispatcher
from src.backend.ocrtranslate.processor import (
    OcrTranslationProcessor,
    OcrTranslationTask,
    ExecutionStrategy
)
import asyncio
from google.protobuf.empty_pb2 import Empty


class OcrTranslateService(
    GRPCService,
    ocrtranslate_pb2_grpc.OcrTranslateServiceServicer
):
    def add_to_server(self, server):
        ocrtranslate_pb2_grpc.add_OcrTranslateServiceServicer_to_server(self, server)

    async def request_recognize(self, request: OcrTranslateRequest, context):
        await self._dispatcher.request_recognize(request)
        return Empty()

    async def stream_results(self, request, context):
        async for result in self._dispatcher.stream_results():
            yield OcrTranslateResult(
                success=True,
                original_text=result.original_text,
                translated_text=result.translated_text
            )


class OcrTranslateDispatcher(UseDispatcher):
    def __init__(self, processor: OcrTranslationProcessor):
        super().__init__()
        self._processor = processor
        self._results = asyncio.Queue()

        async def _on_output(output):
            await self._results.put(output)

        self._processor.add_output_callback(_on_output)

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

    async def stream_results(self):
        while result := await self._results.get():
            yield result
