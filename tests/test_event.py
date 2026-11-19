from src.common.event import EventSystem, IEvent, _DisposableBusEvent
import threading
import pytest


class SampleEvent(IEvent):
    value: int


def test_dispatch_calls_listeners():
    eventsys = EventSystem()
    received = []
    eventsys.listen(lambda event, data: received.append((event, data.value)))

    eventsys.dispatch(SampleEvent, {'value': 1})

    assert received == [(SampleEvent, 1)]


def test_dispatch_outside_owner_thread_raises():
    eventsys = EventSystem()
    errors = []

    def target():
        try:
            eventsys.dispatch(SampleEvent, {'value': 1})
        except RuntimeError as e:
            errors.append(e)

    th = threading.Thread(target=target)
    th.start()
    th.join()

    assert len(errors) == 1


def test_disposable_events_dont_skip_next_handler():
    eventsys = EventSystem()
    calls = []
    eventsys.register(_DisposableBusEvent(SampleEvent, lambda d: calls.append('first'), None))
    eventsys.register(_DisposableBusEvent(SampleEvent, lambda d: calls.append('second'), None))

    eventsys.dispatch(SampleEvent, {'value': 1})
    eventsys.dispatch(SampleEvent, {'value': 2})

    assert calls == ['first', 'second']


def test_disposable_event_removed_when_handler_fails():
    eventsys = EventSystem()
    calls = []

    def handler(data):
        calls.append(data.value)
        raise ValueError('Handler error')

    eventsys.register(_DisposableBusEvent(SampleEvent, handler, None))

    eventsys.dispatch(SampleEvent, {'value': 1})
    eventsys.dispatch(SampleEvent, {'value': 2})

    assert calls == [1]


def test_invalid_event_data_raises():
    eventsys = EventSystem()
    with pytest.raises(ValueError):
        eventsys.dispatch(SampleEvent, {'value': 'wrong type'})
