from src.common.api import KernelAPI
from src.watchdocr.plugins.ocr import OcrPlugin


class OcrAPI(KernelAPI):
    def get_provider_name(self):
        plugins = self.kernel.plugins.get_realizations(OcrPlugin)
        plugins = sorted(plugins, key=lambda e: e.get_priority())
        plugin = plugins[0]
        return plugin.get_provider_name()
