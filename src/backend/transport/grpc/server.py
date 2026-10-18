from src.backend.core.grpc import GRPCServer
from src.backend.transport.grpc.v1.ocrtranslate.service import (
    OcrTranslateService,
    OcrTranslateDispatcher
)
from src.backend.transport.grpc.v1.translation.service import (
    TranslationService,
    TranslationDispatcher
)


class WatchdOcrGRPCServer(GRPCServer):
    pass
