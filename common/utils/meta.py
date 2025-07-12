from typing import Any


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class NoSetAttributeLazy:
    def __init__(self):
        self._block_modify = True

    def __setattr__(self, name: str, value: Any):
        if hasattr(self, '_block_modify'):
            raise PermissionError(
                f'You cannot modify this class {self.__class__.__name__}'
            )
        super().__setattr__(name, value)
