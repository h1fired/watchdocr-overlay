from frontend.common.grpc import GRPCStub
from grpc_proto.v1.ocrtranslate import (
    ocrtranslate_pb2,
    ocrtranslate_pb2_grpc
)


class OcrTranslateStub(GRPCStub):
    def __init__(self, dispatcher):
        super().__init__(dispatcher)
        self._stub = None

    def add_to_channel(self, channel):
        self._stub = ocrtranslate_pb2_grpc.OcrTranslateServiceStub(channel)

    async def stream_results(self):
        call = self._stub.stream_results()
        async for event in call:
            yield event
