from typing import Protocol, runtime_checkable, Callable, Any
from types import SimpleNamespace
from collections import defaultdict
from threading import Lock
from .utils.logging import log


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
        self._lock = Lock()

    def register(self, event: _Event):
        with self._lock:
            self._events[event.interface].append(event)
        return event

    def dispatch(self, event: IEvent, data: dict):
        if type(data) is not dict:
            raise TypeError('Only dict is supported for event data')

        entities = self._events[event]

        for e in entities:
            if not validate_event_data(event, data):
                raise ValueError(f'Event data is not valid -> {event.__name__}')

            namespace = EventData(**data)
            if type(e) is _BusEvent:
                if e.condition(namespace):
                    try:
                        e.handler(namespace)
                    except Exception as e:
                        log.exception(f'[EVENT CALLBACK] {e}')
            elif type(e) is _DisposableBusEvent:
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
                with self._lock:
                    entities.remove(event)
