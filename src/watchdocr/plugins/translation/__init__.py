from src.common.plugin import LaunchPlugin, EventPlugin, PriorityPlugin
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class TranslationData:
    success: bool
    original_text: str
    translated_text: str


class TranslatorPlugin(LaunchPlugin, EventPlugin, PriorityPlugin):
    def translate(self, text: str, _from: str, to: str) -> TranslationData:
        try:
            return self.on_translate(text, _from, to)
        except Exception as e:
            text = f'Failed to translate text! Error: {e}',
            return TranslationData(
                success=False,
                original_text=text,
                translated_text=text
            )

    def on_translate(self, text: str, _from: str, to: str) -> TranslationData:
        raise NotImplementedError

    def get_provider_name(self) -> str:
        return 'Unknown'

    def source_languages(self):
        return {}

    def target_languages(self):
        return {}
