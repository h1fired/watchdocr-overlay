from src.backend.core.grpc import GRPCServer
from src.backend.transport.grpc.v1.ocrtranslate.service import (
    OcrTranslateService,
    OcrTranslateDispatcher
)


class WatchdOcrGRPCServer(GRPCServer):
    pass
