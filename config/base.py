from typing import Any
import inspect
from common.utils.meta import NoSetAttributeLazy
from . import default


def get_module_constants(module) -> dict[str, Any]:
    constants = {}
    for name, value in inspect.getmembers(module):
        if (
            name.isupper() and
            not inspect.isclass(value) and
            not inspect.isfunction(value)
        ):
            constants[name.lower()] = value
    return constants


class AppConfig:
    def load(self):
        default_config = get_module_constants(default)
        return AppConfigOBJ(default_config)


class AppConfigOBJ(NoSetAttributeLazy):
    def __init__(self, config: dict[str, Any]):
        for key, value in config.items():
            setattr(self, key.upper(), value)
        super().__init__()

    def get(self, name: str) -> Any:
        return getattr(self, name.upper())


config = AppConfig().load()
