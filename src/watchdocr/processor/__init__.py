from queue import Queue
from threading import Thread


class WatchdOcrProcessor:
    def __init__(self):
        self._command_q = Queue()
        self._loop_active = False
        self._loop_thread = None

    def start_loop(self):
        self._loop_active = True
        self._loop_thread = Thread(target=self._loop_infinite, daemon=True)
        self._loop_thread.start()

    def stop_loop(self):
        self._loop_active = False
        if self._loop_thread.is_alive():
            self._loop_thread.join()

    def _loop_infinite(self):
        while self._loop_active:
            self._command_q.get()
