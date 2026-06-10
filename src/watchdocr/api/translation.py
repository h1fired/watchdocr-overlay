from src.common.api import KernelAPI
from src.watchdocr.plugins.translation import TranslatorPlugin


class TranslationAPI(KernelAPI):
    def get_provider_name(self):
        plugins = self.kernel.plugins.get_realizations(TranslatorPlugin)
        plugins = sorted(plugins, key=lambda e: e.get_priority())
        plugin = plugins[0]
        return plugin.get_provider_name()

    def get_source_languages(self):
        plugins = self.kernel.plugins.get_realizations(TranslatorPlugin)
        plugins = sorted(plugins, key=lambda e: e.get_priority())
        plugin = plugins[0]
        return plugin.source_languages()

    def get_target_languages(self):
        plugins = self.kernel.plugins.get_realizations(TranslatorPlugin)
        plugins = sorted(plugins, key=lambda e: e.get_priority())
        plugin = plugins[0]
        return plugin.target_languages()

    def set_source_language(self, code: str):
        processor = self.kernel.objects.pull('watchdocr-processor')
        translator = processor.recognizer().translator()
        translator.set_source_language(code)

    def set_target_language(self, code: str):
        processor = self.kernel.objects.pull('watchdocr-processor')
        translator = processor.recognizer().translator()
        translator.set_target_language(code)
