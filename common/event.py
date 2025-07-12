from common.utils.logger import log
from common.utils.schedule import RepeatedTimer
from typing import Protocol, runtime_checkable, Callable, Any
from types import SimpleNamespace
from collections import defaultdict


class EventData(SimpleNamespace):
    pass


@runtime_checkable
class IEvent(Protocol):
    ...


def validate_event_data(obj: IEvent, data: dict):
    fields = obj.__annotations__
    if len(data) != len(fields):
        return False
    for name, _type in fields.items():
        if _type is Any:
            continue
        if name not in data:
            return False
        if type(data[name]) is not _type:
            return False
    return True


class _Event:
    def __init__(self, interface: type[IEvent]):
        if not issubclass(interface, IEvent):
            raise TypeError('Wrong event interface type')
        self._interface = interface

    @property
    def interface(self):
        return self._interface


class _BusEvent(_Event):
    def __init__(self, interface, handler: Callable, condition: Callable):
        super().__init__(interface)
        self._handler = handler
        if not condition:
            self._condition = lambda data: True
        else:
            self._condition = condition

    @property
    def handler(self):
        return self._handler

    @property
    def condition(self):
        return self._condition


class _DisposableBusEvent(_BusEvent):
    pass


class Event:
    @staticmethod
    def subscribe(
        system: 'EventSystem',
        event: IEvent,
        handler: Callable,
        when: Callable = None
    ):
        e = _BusEvent(event, handler, when)
        system.register(e)
        return e

    @staticmethod
    def once(
        system: 'EventSystem',
        event: IEvent,
        handler: Callable,
        when: Callable = None
    ):
        e = _DisposableBusEvent(event, handler, when)
        system.register(e)
        return e


class EventSystem:
    def __init__(self):
        self._events = defaultdict(list)

    def register(self, event: _Event):
        self._events[event.interface].append(event)
        return event

    def dispatch(self, event: IEvent, data: dict):
        if type(data) is not dict:
            raise TypeError('Only dict is supported for event data')

        entities = self._events[event]

        for e in entities:
            if not validate_event_data(event, data):
                raise ValueError('Event data is not valid')

            namespace = EventData(**data)
            if type(e) is _BusEvent:
                if e.condition(namespace):
                    try:
                        e.handler(namespace)
                    except Exception as e:
                        log.exception(f'[EVENT CALLBACK] {e}')
            if type(e) is _DisposableBusEvent:
                if e.condition(namespace):
                    try:
                        e.handler(namespace)
                    except Exception as e:
                        log.exception(f'[EVENT CALLBACK] {e}')
                    finally:
                        entities.remove(e)

    def dispose(self, event: _Event):
        entities = self._events[event.interface]
        for handler in entities:
            if handler == event:
                entities.remove(event)


class Emitter:
    def __init__(self, system: EventSystem, event: IEvent):
        self._system = system
        self._event = event

    def dispatch(self, data: dict):
        self._system.dispatch(self._event, data)


class ThrottledEmitter(Emitter):
    def __init__(self, system, event, interval_ms: int):
        super().__init__(system, event)
        self._freq = interval_ms / 1000.
        self._lt = 0
        self._data = None
        self._updated = False
        self._reload_timer()

    def dispatch(self, data):
        self._data = data
        self._updated = True
        if not self._t.is_alive():
            self._reload_timer()

    def destroy(self):
        self._t.cancel()

    def _interval_dispatch(self):
        if not self._updated:
            self._t.cancel()
        if self._data is not None:
            super().dispatch(self._data)
            self._updated = False

    def _reload_timer(self):
        self._t = RepeatedTimer(self._freq, self._interval_dispatch)
        self._t.daemon = True
        self._t.start()
