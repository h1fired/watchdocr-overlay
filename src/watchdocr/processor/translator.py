from src.common.plugin import PluginManager
from src.watchdocr.plugins.translation import TranslatorPlugin
from src.common.utils.logging import log


class Translator:
    def __init__(self, plugins_manager: PluginManager):
        self._plugins_manager = plugins_manager
        self._source_language = 'EN'
        self._target_language = 'EN'

    def translate(self, text: str, source_lang: str, target_lang: str):
        apis = self._plugins_manager.get_realizations(TranslatorPlugin)
        if not len(apis):
            log.error('No Translation backend plugins found!', extra={'title': 'Translation'})
            raise ValueError('Translator backend plugins not found')
        api = sorted(apis, key=lambda e: e.get_priority())[0]
        return api.translate(text, source_lang, target_lang)
