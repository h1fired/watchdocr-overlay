from src.backend.core.grpc import GRPCService, UseDispatcher
from grpc_proto.v1.translation import translation_pb2_grpc
from grpc_proto.v1.translation.translation_pb2 import LanguagesResponse
from src.backend.ocrtranslate.translator import Translator
from google.protobuf.json_format import ParseDict


class TranslationService(
    GRPCService,
    translation_pb2_grpc.TranslationServiceServicer
):
    def add_to_server(self, server):
        translation_pb2_grpc.add_TranslationServiceServicer_to_server(self, server)

    async def get_languages(self, request, context):
        return self.dispatcher.get_languages()


class TranslationDispatcher(UseDispatcher):
    def __init__(self, translator: Translator):
        super().__init__()
        self._translator = translator

    def get_languages(self):
        languages = self._translator.get_languages()
        response = LanguagesResponse()
        ParseDict(languages, response)
        return response
