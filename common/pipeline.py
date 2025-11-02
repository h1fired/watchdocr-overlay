from common.event import Event, IEvent
from typing import Callable


class Pipeline:
    services: tuple

    def __init__(self, accessor, system):
        self._system = system
        self._services = {cls: accessor(cls) for cls in self.services}
        self._pipeline = self.create_pipeline()
        self._events = []
        self._data = {}
        self._disabled_stages = set()
        self._current_stage = 0

    def get_service(self, service: type):
        return self._services[service]

    def create_pipeline(self):
        raise NotImplementedError

    def create_wrapper(self, stage: int, func: Callable):
        def wrapper(*args, **kwargs):
            normalized_stage = stage + 1
            self._current_stage = normalized_stage
            func(*args, **kwargs)
        return wrapper

    def activate(self):
        for i, (e, func) in enumerate(self._pipeline):
            wrapped_func = self.create_wrapper(i, func)
            e_obj = Event.subscribe(self._system, e, wrapped_func)
            self._events.append(e_obj)

    def deactivate(self):
        for e in self._events:
            self._system.dispose(e)
        self._events.clear()

    def process(self, *args, **kwargs):
        raise NotImplementedError

    def enable_stage(self, stage: int):
        normalized_stage = stage + 1
        if normalized_stage in self._disabled_stages:
            self._disabled_stages.remove(normalized_stage)

    def disable_stage(self, stage: int):
        normalized_stage = stage + 1
        self._disabled_stages.add(normalized_stage)

    def redirect_to(self, event: type[IEvent], data: dict):
        self._system.dispatch(event, data)

    def inject_data(self, stage: int, data: dict):
        normalized_stage = stage + 1
        self._data[normalized_stage] = data

    def get_injected_data(self):
        return self._data.get(self._current_stage, None)
