from src.common.plugin import PluginManager
from src.watchdocr.plugins.translation import TranslatorPlugin


class Translator:
    def __init__(self, plugins_manager: PluginManager):
        self._plugins_manager = plugins_manager

    def translate(self, text: str):
        apis = self._plugins_manager.get_realizations(TranslatorPlugin)
        if not len(apis):
            raise ValueError('Translator backend plugins not found')
        api = apis[0]
        return api.translate(text)
