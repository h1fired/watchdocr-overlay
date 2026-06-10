from src.common.plugin import PluginManager
from src.watchdocr.plugins.translation import TranslatorPlugin


class Translator:
    def __init__(self, plugins_manager: PluginManager):
        self._plugins_manager = plugins_manager
        self._source_language = 'EN'
        self._target_language = 'EN'

    def translate(self, text: str):
        apis = self._plugins_manager.get_realizations(TranslatorPlugin)
        if not len(apis):
            raise ValueError('Translator backend plugins not found')
        api = sorted(apis, key=lambda e: e.get_priority())[0]
        return api.translate(text, self._source_language, self._target_language)

    def set_source_language(self, code: str):
        self._source_language = code

    def set_target_language(self, code: str):
        self._target_language = code
