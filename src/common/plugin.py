from __future__ import annotations
from .event import IEvent, EventSystem, EventData
from .utils.logging import log
from common.observable import MappedObservable
from config import config
from dataclasses import dataclass
from typing import Any, Type, TypeVar, Callable
from collections import defaultdict
import pkgutil
import importlib
import requests
import io
import zipfile
import os
import re


LOG_TITLE = 'Plugins'
_ID_PATTERN = re.compile(r"^[a-z0-9-]+$")


class PluginError(Exception):
    pass


T = TypeVar('T')


class PluginDiscovery:
    def __init__(self):
        self._p_entries = []

    def add_entry_point(self, dir: str):
        log.info('Adding entry point directory: %s', dir, extra={'title': LOG_TITLE})
        self._p_entries.append(dir)

    def discover(self):
        modules = []

        log.info('Starting plugin discovery...', extra={'title': LOG_TITLE})
        for module_path in self._p_entries:
            try:
                package = importlib.import_module(module_path)
            except Exception as e:
                log.error(
                    'Failed to import plugin entry point %s: %s',
                    module_path, e,
                    extra={'title': LOG_TITLE}
                )
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
                    log.error(
                        'Failed to import discovered plugin module %s: %s',
                        name, e,
                        extra={'title': LOG_TITLE}
                    )
                    continue

                if not hasattr(module, '__plugin_meta__'):
                    log.warning(
                        'Module %s is missing __plugin_meta__. Skipping.',
                        name,
                        extra={'title': LOG_TITLE}
                    )
                    continue
                elif not hasattr(module, '__plugin_main__'):
                    log.warning(
                        'Module %s is missing __plugin_main__. Skipping.',
                        name,
                        extra={'title': LOG_TITLE}
                    )
                    continue

                log.info(
                    'Discovered plugin module: %s (id: %s)',
                    name,
                    module.__plugin_meta__.get('id'),
                    extra={'title': LOG_TITLE}
                )
                modules.append(name)

        return tuple(modules)


@dataclass(slots=True, frozen=True)
class PluginMeta:
    id: str
    name: str
    version: tuple[int, int, int]


class PluginManager:
    def __init__(self, eventsys: EventSystem):
        self._eventsys = eventsys
        self._initialized = False
        self._plugins: dict[str, Plugin] = {}

        self._discovery = PluginDiscovery()

    def init(self):
        log.info('Initializing plugins...', extra={'title': LOG_TITLE})
        for name in self._discovery.discover():
            module = importlib.import_module(name)

            id = module.__plugin_meta__['id']
            if id in self._plugins:
                raise ValueError(f'Plugin with id={id} already exists')
            elif not bool(_ID_PATTERN.fullmatch(id)):
                log.warning(
                    (
                        'Module %s meta id is wrong. Only '
                        'lowercase letters, digits and hyphen '
                        'are allowed. Skipping.'
                    ),
                    name,
                    extra={'title': LOG_TITLE}
                )
                continue

            instance = getattr(module, module.__plugin_main__)()
            if isinstance(instance, EventPlugin):
                instance.__eventsys__ = self._eventsys
            if isinstance(instance, LaunchPlugin):
                instance.on_startup()

            meta = PluginMeta(
                id=module.__plugin_meta__['id'],
                name=module.__plugin_meta__['name'],
                version=module.__plugin_meta__['version'],
            )
            instance.__plugin_meta__ = meta
            self._plugins[meta.id] = instance
            log.success(
                'Successfully loaded plugin: %s v%s',
                meta.name, '.'.join(map(str, meta.version)),
                extra={'title': LOG_TITLE}
            )

        # Register on_event callback for event system
        def on_event(event: IEvent, data: EventData):
            for instance in self._plugins:
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
            p for p in self._plugins.values()
            if isinstance(p, plugin)
        ])
        return realizations

    def call_hook(self, id: str, *args, **kwargs):
        for plugin in self.get_realizations(HookPlugin):
            hooks = plugin.__plugin_hooks__.get(id)
            if hooks:
                for hook in hooks:
                    hook(*args, **kwargs)


class Plugin:
    def __str__(self):
        return f'{self.__class__.__name__} ({self.meta.id})'

    @property
    def meta(self) -> PluginMeta:
        return self.__plugin_meta__


# Plugin types
class HookPlugin(Plugin):
    def __init_subclass__(cls):
        super().__init_subclass__()

        cls.__plugin_hooks__ = defaultdict(set)
        for _, attr in cls.__dict__.items():
            if hasattr(attr, '__hook_id__'):
                cls.__plugin_hooks__[attr.__hook_id__].add(attr)


def hook(id: str):
    def decorator(func):
        func.__hook_id__ = id
        return func
    return decorator


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

        log_title = self.meta.name

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
            self.meta.id
        )


class PluginResourceDownloader:
    def __init__(self, manager: PluginManager):
        self._manager = manager
        self._observable = MappedObservable()

    def start_download(self):
        plugins = self._manager.get_realizations(DownloadablePlugin)

        try:
            length = len(plugins)
            for index, plugin in enumerate(plugins):
                plugin.download_resource()
                plugin.on_after_download()
                progress = round(index+1 / length, 1)
                self._observable.notify('progress', progress)
                return True
        except Exception as e:
            log.error('An error occurred. %s', e, extra={'title': LOG_TITLE})
            return False

    def observe(self, trigger: str, callback: Callable):
        self._observable.register(trigger, callback)
