from common.service import Service
from common.event import IEvent
from src.translator.translate import Translator


class _TranslationOutputReceiveEvent(IEvent):
    output: dict


class TranslationService(Service):

    class Events:
        OUTPUT_RECEIVE = _TranslationOutputReceiveEvent

    def on_init(self):
        self._translator = Translator()

    def translate(self, text: str, _from: str, to: str):
        text = self._translator.translate(text, _from, to)
        self.event.dispatch(self.Events.OUTPUT_RECEIVE, {'output': text})
        return text

    def backends(self):
        return self._translator.backends()

    def propagate_shared_objects(self):
        return {'translator': self._translator}
