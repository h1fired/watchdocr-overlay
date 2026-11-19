from src.common.event import EventSystem, IEvent
from src.common.plugin import (
    PluginManager,
    PluginMeta,
    HookPlugin,
    EventPlugin,
    LaunchPlugin,
    hook
)
import asyncio


class SampleEvent(IEvent):
    value: int


class SyncHookPlugin(HookPlugin):
    @hook('test.hook')
    def on_hook(self, data):
        return data + '-sync'


class AsyncHookPlugin(HookPlugin):
    @hook('test.hook')
    async def on_hook(self, data):
        await asyncio.sleep(0)
        return data + '-async'


class RecordingEventPlugin(EventPlugin):
    def __init__(self):
        self.events = []

    def on_event(self, event, data):
        self.events.append(event)


class RecordingLaunchPlugin(LaunchPlugin):
    def __init__(self):
        self.calls = []

    async def on_startup(self):
        self.calls.append('startup')

    async def on_shutdown(self):
        self.calls.append('shutdown')


class FailingLaunchPlugin(LaunchPlugin):
    async def on_shutdown(self):
        raise ValueError('Shutdown error')


def create_manager(plugins: dict):
    eventsys = EventSystem()
    manager = PluginManager(eventsys)
    manager.init()  # No entry points, nothing to discover
    manager._plugins = plugins
    return manager, eventsys


async def test_call_hook_supports_sync_and_async_hooks():
    manager, _ = create_manager({
        'sync': SyncHookPlugin(),
        'async': AsyncHookPlugin()
    })

    result = await manager.call_hook('test.hook', 'data')

    assert result == 'data-sync-async'


async def test_call_hook_without_hooks_returns_data():
    manager, _ = create_manager({'sync': SyncHookPlugin()})

    result = await manager.call_hook('test.unknown_hook', 'data')

    assert result == 'data'


def test_event_plugins_receive_events():
    plugin = RecordingEventPlugin()
    _, eventsys = create_manager({'recording': plugin})

    eventsys.dispatch(SampleEvent, {'value': 1})

    assert plugin.events == [SampleEvent]


async def test_plugins_lifecycle():
    failing = FailingLaunchPlugin()
    failing.__plugin_meta__ = PluginMeta(id='failing', name='Failing', version=(0, 1, 0))
    recording = RecordingLaunchPlugin()
    manager, _ = create_manager({'failing': failing, 'recording': recording})

    await manager.start()
    await manager.shutdown()  # Failing plugin must not break shutdown of others

    assert recording.calls == ['startup', 'shutdown']
