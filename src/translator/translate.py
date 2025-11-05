from common.task import TaskManager
from common.observable import TypedObservable
from src.translator.backend import TranslationBackendManager, TranslationStatus
from src.translator.backend.deepl import DeeplTranslationBackend
from src.translator.backend.google import GoogleTranslationBackend


backends = [
    DeeplTranslationBackend,
    GoogleTranslationBackend
]


class Translator:
    def __init__(self):
        self._backends = TranslationBackendManager(backends)
        self._task_id = 'task.translator.translate'
        self._obs_data = TypedObservable(dict)

    def translate(self, text: str, _from: str, to: str):
        future = TaskManager.execute(
            task=lambda _: self.worker(text, _from, to),
            id=self._task_id
        )
        future.observe(on_result=self._obs_data.notify)

    def terminate(self):
        if TaskManager.objects().exists(self._task_id):
            task = TaskManager.objects().get(self._task_id)
            task.cancel()
            task.wait()

    def backends(self):
        return self._backends

    def worker(self, text, _from, to):
        backend = self._backends.current().value
        return backend.translate(text, _from, to)

    def observable(self):
        return self._obs_data
