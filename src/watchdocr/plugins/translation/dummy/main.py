from src.watchdocr.plugins.translation import TranslatorPlugin, TranslationData


__plugin_meta__ = {
    'id': 'watchdocr.translator.dummy',
    'name': 'DummyTranslator',
    'version': (0, 1, 0)
}
__plugin_main__ = 'DummyTranslatorPlugin'


class DummyTranslatorPlugin(TranslatorPlugin):
    def translate(self, text):
        return TranslationData(text, f'translated({text})')
