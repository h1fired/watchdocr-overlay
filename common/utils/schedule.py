import time
import threading


class Timeout:
    def __init__(self, timeout: float):
        self._timeout = timeout * 1e9
        self.__timestamp = time.perf_counter_ns()

    def is_expired(self):
        if time.perf_counter_ns() > self.__timestamp + self._timeout:
            return True
        return False

    def reset(self):
        self.__timestamp = time.perf_counter_ns()

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        self._timeout = value


class PeriodicTrigger:
    def __init__(self, frequency):
        self.frequency = float(frequency)
        self.last_time = time.monotonic()

    def set_frequency(self, frequency: float):
        self.frequency = frequency

    def force(self):
        self.last_time = 0

    def should_trigger(self):
        tnow = time.monotonic()

        if tnow < self.last_time:
            self.last_time = tnow

        if self.last_time + (1.0 / self.frequency) <= tnow:
            self.last_time = tnow
            return True
        return False


class RepeatedTimer(threading.Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
