from contextlib import contextmanager
import time


class Stopwatch:
    '''Measures named laps and total time since creation'''

    def __init__(self):
        self._start = time.perf_counter()
        self._laps: dict[str, float] = {}

    @contextmanager
    def measure(self, name: str):
        start = time.perf_counter()
        try:
            yield
        finally:
            self._laps[name] = time.perf_counter() - start

    def summary(self):
        laps = ', '.join(
            f'{name}={seconds * 1000:.1f}ms'
            for name, seconds in self._laps.items()
        )
        total = (time.perf_counter() - self._start) * 1000
        return f'{laps}, total={total:.1f}ms'
