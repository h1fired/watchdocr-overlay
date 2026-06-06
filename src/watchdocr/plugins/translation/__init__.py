from src.common.plugin import LaunchPlugin, EventPlugin
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class TranslationData:
    original_text: str
    translated_text: str


class TranslatorPlugin(LaunchPlugin, EventPlugin):
    def translate(self, text: str) -> TranslationData:
        raise NotImplementedError
