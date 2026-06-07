from src.common.plugin import LaunchPlugin, EventPlugin, PriorityPlugin
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class TranslationData:
    original_text: str
    translated_text: str


class TranslatorPlugin(LaunchPlugin, EventPlugin, PriorityPlugin):
    def translate(self, text: str, _from: str, to: str) -> TranslationData:
        raise NotImplementedError

    def source_languages(self):
        return {}

    def target_languages(self):
        return {}
