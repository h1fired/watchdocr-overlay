from frontend.viewmodels.common.mvvm import QmlViewModel
from src.watchdocr.api.translation import TranslationAPI
from src.watchdocr.plugins.translation.types import LANGUAGES_VERBOSE
from qt.core import Property, Signal, Slot
import json


class TranslationViewModel(QmlViewModel):
    _name = 'Translation'
    _needed_api = (TranslationAPI,)

    sourceLanguagesChanged = Signal()
    targetLanguagesChanged = Signal()

    def getSourceLanguages(self):
        api = self.getApi(TranslationAPI)
        languages = [
            {'code': k, 'name': LANGUAGES_VERBOSE.get(k, 'Unknown')}
            for k in api.get_source_languages().keys()
        ]
        return json.dumps(languages)

    sourceLanguages = Property(str, getSourceLanguages, notify=sourceLanguagesChanged)

    def getTargetLanguages(self):
        api = self.getApi(TranslationAPI)
        languages = [
            {'code': k, 'name': LANGUAGES_VERBOSE.get(k, 'Unknown')}
            for k in api.get_target_languages().keys()
        ]
        return json.dumps(languages)

    targetLanguages = Property(str, getTargetLanguages, notify=targetLanguagesChanged)

    @Slot(str)
    def setSourceLanguage(self, code: str):
        api = self.getApi(TranslationAPI)
        api.set_source_language(code)

    @Slot(str)
    def setTargetLanguage(self, code: str):
        api = self.getApi(TranslationAPI)
        api.set_target_language(code)
