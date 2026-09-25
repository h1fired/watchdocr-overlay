from . import ocrtranslate_pb2, ocrtranslate_pb2_grpc
from ocrtranslate_pb2 import OcrTranslateRequest
from src.backend.core.grpc import GRPCService, UseDispatcher


class OcrTranslateService(
    GRPCService,
    ocrtranslate_pb2_grpc.OcrTranslateServiceServicer
):
    def request_recognize(self, request: OcrTranslateRequest, context):
        self._dispatcher.request_recognize(request)


class OcrTranslateDispatcher(UseDispatcher):

    def request_recognize(self, request: OcrTranslateRequest):
        print('DISPATCHER', request)
