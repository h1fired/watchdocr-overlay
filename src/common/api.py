from typing import Type, TypeVar


T = TypeVar('KernelAPI')


class KernelAPI:
    def __init__(self, kernel):
        self._kernel = kernel


class KernelAPICollection:
    def __init__(self):
        self._components: dict[Type[KernelAPI], KernelAPI] = {}

    def add(self, api: KernelAPI):
        self._components[type(api)] = api

    def all(self):
        return tuple(self._components.values())


class KernelAPIStrictCollection:
    def __init__(self, components: tuple[KernelAPI, ...] = tuple()):
        self._components = {type(c): c for c in components}

    def get(self, api: Type[T]) -> T:
        return self._components[api]
