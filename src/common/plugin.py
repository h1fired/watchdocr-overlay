from __future__ import annotations
from typing import Any
from .event import IEvent, EventSystem, EventData


class PluginManager:
    def __init__(self):
        self._eventsys = EventSystem()
        self._initialized = False
        self._plugins_types = []
        self._plugins = []

    def init(self):
        for plugin in self._plugins_types:
            obj = plugin()
            if isinstance(obj, EventPlugin):
                obj.__eventsys__ = self._eventsys
            if isinstance(obj, LaunchPlugin):
                obj.on_startup()
            self._plugins.append(obj)

        self._eventsys.listen(self.on_event)

    def add_plugin(self, plugin: type[Plugin]):
        if self._initialized:
            raise RuntimeError('Cannot add plugin when manager initialized')
        self._plugins_types.append(plugin)

    def on_event(self, event: IEvent, data: EventData):
        for plugin in self._plugins:
            if isinstance(plugin, EventPlugin):
                plugin.on_event(event, data)


class Plugin:
    _id: str = ''

    def __str__(self):
        return f'{self.__class__.__name__} ({self._id})'


class LaunchPlugin(Plugin):
    def on_startup(self):
        pass


class EventPlugin(Plugin):
    __eventsys__: EventSystem = None

    def on_event(self, event: IEvent, data: EventData):
        pass

    def fire(self, event: IEvent, data: dict[str, Any]):
        self.__eventsys__.dispatch(event, data)


class SwitchablePlugin(Plugin):
    pass
