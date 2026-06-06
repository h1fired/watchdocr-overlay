from __future__ import annotations
from typing import Any, Type, TypeVar
from .event import IEvent, EventSystem, EventData
import pkgutil
import importlib


T = TypeVar('T')


class PluginDiscovery:
    def __init__(self):
        self._p_entries = []

    def add_entry_point(self, dir: str):
        self._p_entries.append(dir)

    def discover(self):
        modules = []

        for module_path in self._p_entries:
            package = importlib.import_module(module_path)
            for _, name, _ in pkgutil.walk_packages(
                path=package.__path__,
                prefix=package.__name__ + '.',
            ):
                if not name.endswith('.main'):
                    continue

                module = importlib.import_module(name)

                if not hasattr(module, '__plugin_meta__'):
                    continue
                elif not hasattr(module, '__plugin_main__'):
                    continue
                modules.append(name)

        return tuple(modules)


class PluginMeta:
    def __init__(
        self,
        id: str,
        name: str,
        version: tuple[int, int, int],
        instance: Plugin
    ):
        self._id = id
        self._name = name
        self._version = version
        self._instance = instance

    def id(self):
        return self._id

    def name(self):
        return self._name

    def version(self):
        return self._version

    def instance(self):
        return self._instance


class PluginManager:
    def __init__(self, eventsys: EventSystem):
        self._eventsys = eventsys
        self._initialized = False
        self._plugins: list[PluginMeta] = []

        self._discovery = PluginDiscovery()

    def init(self):
        for name in self._discovery.discover():
            module = importlib.import_module(name)

            instance = getattr(module, module.__plugin_main__)()
            if isinstance(instance, EventPlugin):
                instance.__eventsys__ = self._eventsys
            if isinstance(instance, LaunchPlugin):
                instance.on_startup()

            meta = PluginMeta(
                module.__plugin_meta__['id'],
                module.__plugin_meta__['name'],
                module.__plugin_meta__['version'],
                instance=instance
            )
            self._plugins.append(meta)

        # Register on_event callback for event system
        def on_event(event: IEvent, data: EventData):
            for plugin in self._plugins:
                instance = plugin.instance()
                if isinstance(instance, EventPlugin):
                    instance.on_event(event, data)
        self._eventsys.listen(on_event)

    def add_entry_point(self, dir: str):
        if self._initialized:
            raise RuntimeError('Cannot add plugin when manager initialized')
        self._discovery.add_entry_point(dir)

    def get_realizations(self, plugin: Type[T]) -> tuple[T, ...]:
        return tuple([
            p.instance() for p in self._plugins
            if isinstance(p.instance(), plugin)
        ])


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
