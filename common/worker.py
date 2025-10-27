from typing import Callable
from enum import IntEnum
from threading import Thread, Event, Lock
from .observable import Observer


class WorkerState(IntEnum):
    WAIT = 0
    ERROR = 1
    FINISHED = 2


class Worker:
    daemon = False

    def __init__(self):
        super().__init__()
        self.stop_event = Event()
        self._thread = None
        self._lock = Lock()

    def start(self, *args):
        if self.is_alive():
            raise RuntimeError('Worker is already started')

        self.stop_event.clear()
        self._thread = Thread(target=self.run, args=args, daemon=self.daemon)
        self._thread.start()

    def stop(self):
        if not self.is_alive():
            raise RuntimeError('Worker is already stopped')

        self.stop_event.set()

    def is_alive(self):
        return self._thread and self._thread.is_alive()

    def join(self):
        if not self.is_alive():
            raise RuntimeError('Worker is not started')

        self._thread.join()

    def run(self, *args):
        raise NotImplementedError('Worker task not implemented')


class ObservableWorker(Worker):
    def __init__(self):
        super().__init__()
        self.signal = Observer()
        self._observer = Observer()

    def send_observable_data(self, *args, **kwargs):
        with self._lock:
            self._observer.notify(*args, **kwargs)

    def on_data(self, callback: Callable):
        with self._lock:
            self._observer.register(callback)

    def on_signal(self, callback: Callable):
        with self._lock:
            self.signal.register(callback)
