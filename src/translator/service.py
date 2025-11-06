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
        self._translator.observable().register(self._on_data)

    def translate(self, text: str, _from: str, to: str):
        self._translator.translate(text, _from, to)

    def backends(self):
        return self._translator.backends()

    def propagate_shared_objects(self):
        return {'translator': self._translator}

    def _on_data(self, output: dict):
        self.event.dispatch(
            event=self.Events.OUTPUT_RECEIVE,
            data={'output': output}
        )
