from __future__ import annotations
from .event import IEvent, EventSystem, EventData
from .utils.logging import log
from common.observable import MappedObservable
from config import config
from dataclasses import dataclass
from typing import Any, Type, TypeVar, Callable
import pkgutil
import importlib
import requests
import io
import zipfile
import os


T = TypeVar('T')


class PluginError(Exception):
    pass


class PluginDiscovery:
    def __init__(self):
        self._p_entries = []

    def add_entry_point(self, dir: str):
        log.info('Adding entry point directory: %s', dir, extra={'title': 'Plugins'})
        self._p_entries.append(dir)

    def discover(self):
        modules = []

        log.info('Starting plugin discovery...', extra={'title': 'Plugins'})
        for module_path in self._p_entries:
            try:
                package = importlib.import_module(module_path)
            except Exception as e:
                log.error('Failed to import plugin entry point %s: %s', module_path, e, extra={'title': 'Plugins'})
                continue

            for _, name, _ in pkgutil.walk_packages(
                path=package.__path__,
                prefix=package.__name__ + '.',
            ):
                if not name.endswith('.main'):
                    continue

                try:
                    module = importlib.import_module(name)
                except Exception as e:
                    log.error('Failed to import discovered plugin module %s: %s', name, e, extra={'title': 'Plugins'})
                    continue

                if not hasattr(module, '__plugin_meta__'):
                    log.warning('Module %s is missing __plugin_meta__. Skipping.', name, extra={'title': 'Plugins'})
                    continue
                elif not hasattr(module, '__plugin_main__'):
                    log.warning('Module %s is missing __plugin_main__. Skipping.', name, extra={'title': 'Plugins'})
                    continue

                log.info('Discovered plugin module: %s (id: %s)', name, module.__plugin_meta__.get('id'), extra={'title': 'Plugins'})
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
        log.info('Initializing plugins...', extra={'title': 'Plugins'})
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
            log.success('Successfully loaded plugin: %s v%s', meta.name(), '.'.join(map(str, meta.version())), extra={'title': 'Plugins'})

        # Register on_event callback for event system
        def on_event(event: IEvent, data: EventData):
            for plugin in self._plugins:
                instance = plugin.instance()
                if isinstance(instance, EventPlugin):
                    instance.on_event(event, data)
        self._eventsys.listen(on_event)
        self._initialized = True

    def add_entry_point(self, dir: str):
        if self._initialized:
            raise RuntimeError('Cannot add plugin when manager initialized')
        self._discovery.add_entry_point(dir)

    def get_realizations(self, plugin: Type[T]) -> tuple[T, ...]:
        realizations = tuple([
            p.instance() for p in self._plugins
            if isinstance(p.instance(), plugin)
        ])
        return realizations


class PluginResourceDownloader:
    def __init__(self, manager: PluginManager):
        self._manager = manager
        self._observable = MappedObservable()

    def start_download(self):
        plugins = self._manager.get_realizations(DownloadablePlugin)

        length = len(plugins)
        try:
            for index, plugin in enumerate(plugins):
                progress = round(index+1 / length, 1)
                self._observable.notify('progress', progress)
                plugin.download_resource()
                plugin.on_after_download()
            self._observable.notify('success')
        except Exception as e:
            self._observable.notify('error', e)
        self._observable.notify('finished')

    def observe(self, trigger: str, callback: Callable):
        self._observable.register(trigger, callback)


class Plugin:
    _id: str = ''

    def __str__(self):
        return f'{self.__class__.__name__} ({self._id})'

    def get_name(self):
        return self._id


class LaunchPlugin(Plugin):
    def on_startup(self):
        pass


class EventPlugin(Plugin):
    __eventsys__: EventSystem = None

    def on_event(self, event: IEvent, data: EventData):
        pass

    def fire(self, event: IEvent, data: dict[str, Any]):
        self.__eventsys__.dispatch(event, data)


class PriorityPlugin(Plugin):
    def get_priority(self):
        return 0


@dataclass(slots=True)
class DownloadResource:
    url: str


RESOURCE_EXISTS_FILENAME = '.ready'


class DownloadablePlugin(Plugin):
    def on_after_download(self):
        pass

    def download_resource(self):
        rpath = self.get_resource_path()
        resource_exists_file_path = os.path.join(rpath, RESOURCE_EXISTS_FILENAME)

        log_title = self.get_name()

        if os.path.exists(resource_exists_file_path):
            log.info(
                'Resource data already downloaded. Get cached',
                extra={'title': log_title}
            )
            return

        try:
            resource = self.get_download_resource()
            log.info(
                'Trying to download resource data from: %s', resource.url,
                extra={'title': log_title}
            )
            r = requests.get(url=resource.url)

            if r.ok:
                zip = zipfile.ZipFile(io.BytesIO(r.content))
                zip.extractall(rpath)

                # Create create file for checking
                # if data is already downloaded
                with open(resource_exists_file_path, 'w'):
                    pass

            log.info(
                'Resource data successfully downloaded',
                extra={'title': log_title}
            )
        except Exception as e:
            raise PluginError('Failed to download resource') from e

    def get_download_resource(self) -> DownloadResource:
        raise NotImplementedError

    def get_resource_path(self):
        return os.path.join(
            config.PLUGINS_DOWNLOAD_DATA_PATH,
            self.get_name()
        )
