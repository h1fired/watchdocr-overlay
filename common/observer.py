from typing import Callable
from collections import defaultdict
from threading import Lock
from .utils.logger import log


class Observer:
    def __init__(self):
        self._lock = Lock()
        self._notifiers: list[Callable] = []

    def register(self, callback: Callable):
        with self._lock:
            self._notifiers.append(callback)

    def unregister(self, callback: Callable):
        with self._lock:
            self._notifiers.remove(callback)

    def notify(self, *args, **kwargs):
        with self._lock:
            for notifier in self._notifiers:
                try:
                    notifier(*args, **kwargs)
                except Exception as e:
                    log.exception(f'[CALLBACK] {e}')


class MappedObserver:
    def __init__(self):
        self._lock = Lock()
        self._notifiers = defaultdict(list)

    def register(self, subject: str, callback: Callable):
        with self._lock:
            self._notifiers[subject].append(callback)

    def notify(self, subject: str, *args, **kwargs):
        with self._lock:
            if subject not in self._notifiers.keys():
                return
            for notifier in self._notifiers[subject]:
                try:
                    notifier(*args, **kwargs)
                except Exception as e:
                    log.exception(f'[CALLBACK] {e}')


def bind_observer_to_map(
    observer: Observer,
    map: MappedObserver,
    subject: str
):
    observer.register(lambda *data: map.notify(subject, *data))
