import asyncio
import numpy as np
from google.protobuf.empty_pb2 import Empty
from grpc_interceptor.exceptions import InvalidArgument
from grpc_proto.v1.ocrtranslate import ocrtranslate_pb2_grpc
from grpc_proto.v1.ocrtranslate.ocrtranslate_pb2 import (
    OcrTranslateRequest,
    OcrTranslateResult
)
from src.backend.transport.grpc.server import GRPCService, UseDispatcher
from src.backend.ocrtranslate.processor import (
    OcrTranslationProcessor,
    OcrTranslationTask,
    ExecutionStrategy
)


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
                translated_text=result.translated_text,
                boxes=np.asarray(result.boxes, dtype='<i4').tobytes(),
                original_parts=result.original_parts,
                translated_parts=result.translated_parts,
                confidence=result.total_confidence
            )


class OcrTranslateDispatcher(UseDispatcher):
    _ALLOWED_METHODS = {
        'all',
        'ocr_only',
        'retranslate',
    }

    def __init__(self, processor: OcrTranslationProcessor):
        super().__init__()
        self._processor = processor
        self._results = asyncio.Queue()

        async def _on_output(output):
            await self._results.put(output)

        self._processor.add_output_callback(_on_output)

    async def request_recognize(self, request: OcrTranslateRequest):
        if request.strategy not in ExecutionStrategy._value2member_map_:
            raise InvalidArgument(f'Unknown strategy: {request.strategy}')
        method = request.WhichOneof('method')
        if method not in self._ALLOWED_METHODS:
            raise InvalidArgument(f'Unknown method: {request.strategy}')

        context_data = {}
        match method:
            case 'all':
                context_data.update({
                    'image_capture': {
                        'box': request.all.bounding
                    },
                    'translation': {
                        'source_language': request.all.source_language,
                        'target_language': request.all.target_language
                    }
                })
            case 'ocr_only':
                context_data.update({
                    'image_capture': {
                        'box': request.ocr_only.bounding
                    },
                })
            case 'retranslate':
                context_data.update({
                    'ocr': {
                        'success': True,
                        'text': request.retranslate.text
                    },
                    'translation': {
                        'source_language': request.retranslate.source_language,
                        'target_language': request.retranslate.target_language
                    }
                })

        task = OcrTranslationTask(
            strategy=ExecutionStrategy(request.strategy),
            context_data=context_data
        )
        await self._processor.request(task)

    async def stream_results(self):
        while result := await self._results.get():
            yield result
