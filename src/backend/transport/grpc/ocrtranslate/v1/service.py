from . import ocrtranslate_pb2, ocrtranslate_pb2_grpc
from ocrtranslate_pb2 import OcrTranslateRequest
from src.backend.core.grpc import GRPCService


class OcrTranslateService(
    GRPCService,
    ocrtranslate_pb2_grpc.OcrTranslateServiceServicer
):
    def request_recognize(self, request: OcrTranslateRequest, context):
        return ocrtranslate_pb2.Empty()
