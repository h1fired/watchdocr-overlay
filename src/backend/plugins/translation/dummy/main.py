from src.backend.plugins.translation import TranslatorPlugin, TranslationData


__plugin_meta__ = {
    'id': 'watchdocr-translator-dummy',
    'name': 'DummyTranslator',
    'version': (0, 1, 0)
}
__plugin_main__ = 'DummyTranslatorPlugin'


SOURCE_LANGUAGES = {'TEST': 'test'}
TARGET_LANGUAGES = {'TEST': 'test'}
VERBOSE_LANGUAGES = {'TEST': 'Test'}


class DummyTranslatorPlugin(TranslatorPlugin):
    def on_translate(self, text, _from, to):
        translated = f'translated({text})[{_from}->{to}]'
        return TranslationData(
            success=True,
            original_text=text,
            translated_text=translated
        )

    def get_priority(self):
        return 1

    def get_provider_name(self):
        return 'Dummy'

    def source_languages(self):
        return SOURCE_LANGUAGES

    def target_languages(self):
        return TARGET_LANGUAGES

    def versobe_languages(self):
        return VERBOSE_LANGUAGES
