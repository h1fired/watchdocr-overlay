from src.common.plugin import HookPlugin, hook
import re


def cleanup_text_simple(text: str):
    ctext = re.sub(r'[ \t]+', ' ', text)  # Clean multiple whitespaces
    return ctext


__plugin_meta__ = {
    'id': 'watchdocr-textfilter',
    'name': 'TextFilter',
    'version': (0, 1, 0)
}
__plugin_main__ = 'TextFilterPlugin'


class TextFilterPlugin(HookPlugin):

    @hook('watchdocr.translation_pipeline.output_text')
    def on(self, text: str):
        ctext = cleanup_text_simple(text)
        return ctext
