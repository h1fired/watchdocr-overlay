from __future__ import annotations
from .event import IEvent, EventSystem, EventData
from .utils.logging import log
from common.observable import MappedObservable
from config import config
from dataclasses import dataclass
from typing import Any, Type, TypeVar, Callable
from collections import defaultdict
from contextlib import suppress
import pkgutil
import importlib
import requests
import zipfile
import os
import re
import hashlib


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

    def call_hook(self, id: str, data: Any, *args, **kwargs):
        for plugin in self.get_realizations(HookPlugin):
            hooks = plugin.__plugin_hooks__.get(id)
            if hooks:
                for hook in hooks:
                    data = hook(plugin, data, *args, **kwargs)
        return data


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
    sha256: str | None = None


RESOURCE_EXISTS_FILENAME = '.ready'
DOWNLOAD_CHUNK_SIZE = 1024*128
DOWNLOAD_TIMEOUT = 10


def file_sha256_sum(filename: str):
    h = hashlib.sha256()
    b = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
    return h.hexdigest()


class DownloadablePlugin(Plugin):
    def on_after_download(self):
        pass

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

    def start_download(self) -> bool:
        plugins = self._manager.get_realizations(DownloadablePlugin)

        length = len(plugins)
        if not length:
            return True

        for index, plugin in enumerate(plugins, start=1):
            try:
                self._download_plugin(plugin, index, length)
            except Exception:
                log.exception(
                    'Failed to download plugin %s', plugin.meta.name,
                    extra={'title': LOG_TITLE},
                )
                return False

        return True

    def observe(self, trigger: str, callback: Callable):
        self._observable.register(trigger, callback)

    def _download_plugin(
        self,
        plugin: DownloadablePlugin,
        index: int,
        total: int
    ):
        resource = plugin.get_download_resource()
        download_path = plugin.get_resource_path()

        last_progress = None
        for total_size, current_size in self._download_resource(resource, download_path):
            progress = self._calculate_progress(index, total, total_size, current_size)
            if progress != last_progress:
                self._observable.notify('progress', progress)
                last_progress = progress

        plugin.on_after_download()

    def _download_resource(
        self,
        download_res: DownloadResource,
        download_path: str
    ):
        checkfile_path = os.path.join(download_path, RESOURCE_EXISTS_FILENAME)
        if os.path.exists(checkfile_path):
            yield 0, 0
            return

        os.makedirs(download_path, exist_ok=True)
        archive_path = os.path.join(
            download_path,
            f'.{config.APP_NAME.lower()}_cache'
        )

        try:
            yield from self._stream_download(download_res.url, archive_path)

            if download_res.sha256:
                self._verify_sha256(archive_path, download_res.sha256)

            self._extract_archive(archive_path, download_path)
        finally:
            with suppress(OSError):
                os.remove(archive_path)

        with open(checkfile_path, 'w'):
            pass

    def _stream_download(self, url: str, dest_path: str):
        with requests.get(url, stream=True, timeout=DOWNLOAD_TIMEOUT) as r:
            r.raise_for_status()

            total_size = int(r.headers.get('content-length') or 0)

            with open(dest_path, 'wb') as f:
                bytes_downloaded = 0
                for chunk in r.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                    f.write(chunk)
                    bytes_downloaded += len(chunk)

                    yield total_size, bytes_downloaded

    def _verify_sha256(self, filename: str, expected: str):
        actual_sum = file_sha256_sum(filename)
        if actual_sum != expected:
            raise PluginError(f'SHA256 mismatch, expected {expected}, got {actual_sum}')

    def _extract_archive(self, path: str, dest: str):
        with zipfile.ZipFile(path) as archive:
            archive.extractall(dest)

    def _calculate_progress(
        self,
        index: str,
        total_indexes: int,
        total_bytes: int,
        current_bytes: int
    ):
        if index <= 0:
            return 0.

        progress_per_index = 1. / total_indexes
        curr_index_progress = progress_per_index * (index - 1)

        try:
            size_progress = current_bytes / total_bytes
        except ZeroDivisionError:
            size_progress = 1.

        progress = curr_index_progress + (size_progress * progress_per_index)
        return round(progress, 2)
