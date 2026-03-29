from enum import IntEnum
from dataclasses import dataclass, asdict
from threading import Thread, Condition
from typing import Callable


class RecognizerMode(IntEnum):
    ONETIME = 0
    LIVE = 1


@dataclass(slots=True)
class RecognizerResult:
    original_text: str
    translated_text: str

    def to_dict(self):
        return asdict(self)


class Recognizer:
    def __init__(self):
        self._loop_active = False
        self._thread = None
        self._w = Condition()
        self._live_freq = 1.0
        self._result_callback = None

        self._active = False
        self._mode = RecognizerMode.ONETIME
        self._box = (0, 0, 0, 0)

    def run(self):
        self._loop_active = True
        self._thread = Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._loop_active = False
        self.interrupt()
        if self._thread.is_alive():
            self._thread.join()
        self._thread = None

    def interrupt(self):
        with self._w:
            self._w.notify_all()

    def refresh(self):
        with self._w:
            self._w.notify_all()

    def is_active(self):
        return self._active

    def set_active(self, value: bool):
        self._active = value

    def mode(self):
        return self._mode

    def set_mode(self, mode: RecognizerMode):
        self._mode = mode

    def set_live_mode_frequency(self, freq: float):
        self._live_freq = freq

    def set_area(self, box: tuple[int, int, int, int]):
        self._box = box

    def register_callback(self, callback: Callable):
        self._result_callback = callback

    def _loop(self):
        counter = 0

        while self._loop_active:
            if not self._active:
                with self._w:
                    self._w.wait()

            if self._result_callback:
                counter += 1
                res = RecognizerResult(
                    f'text - {self._mode.name} - {self._box} - {counter}',
                    f'текст - {self._mode.name} - {self._box} - {counter}',
                )
                self._result_callback(res)

            with self._w:
                if self._mode == RecognizerMode.LIVE:
                    self._w.wait(self._live_freq)
                else:
                    self._w.wait()
