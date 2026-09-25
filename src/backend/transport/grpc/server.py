from src.backend.core.grpc import GRPCServer
from src.backend.transport.grpc.ocrtranslate.v1.service import (
    OcrTranslateService,
    OcrTranslateDispatcher
)


services = [
    (OcrTranslateService, OcrTranslateDispatcher),
]


class WatchdOcrGRPCServer(GRPCServer):
    pass
