from frontend.common.grpc import GRPCStub
from grpc_proto.v1.ocrtranslate import (
    ocrtranslate_pb2,
    ocrtranslate_pb2_grpc
)
from google.protobuf.empty_pb2 import Empty


class OcrTranslateStub(GRPCStub):
    def __init__(self):
        super().__init__()
        self._stub = None

    def add_to_channel(self, channel):
        self._stub = ocrtranslate_pb2_grpc.OcrTranslateServiceStub(channel)

    async def stream_results(self):
        call = self._stub.stream_results(Empty())
        async for event in call:
            yield event

    async def request_recognize(self, bounding: tuple[int, int, int, int]):
        req = ocrtranslate_pb2.OcrTranslateRequest(bounding=bounding)
        await self._stub.request_recognize(req)
