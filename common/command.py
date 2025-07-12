from .utils.logger import log
from .utils.meta import Singleton
from .service import ServicesAccessor
from .task import TaskManager
from typing import Callable


class Command:
    name: str

    def execute(self, accessor: ServicesAccessor, *data):
        try:
            log.info(f'[COMMAND] Command {self.name} executed')
            self.executable(accessor, *data)
        except Exception as e:
            log.exception(f'[COMMAND] Command {self.name} executed with error {e}')

    def executable(self, accessor: ServicesAccessor, *data):
        raise NotImplementedError('Command not implemented')

    def reject(self, reason: str):
        log.error(
            f'[COMMAND] Command {self.name} rejected. '
            f'Reason: {reason}'
        )


class AsyncCommand(Command):

    @classmethod
    def task_id(cls):
        return f'command.{cls.name}'

    def execute(self, accessor: ServicesAccessor, *data):
        try:
            if not self.task_id:
                raise ValueError('task_id is not setted')

            log.info(f'[COMMAND] Command {self.name} executed')

            manager = TaskManager()
            manager.execute(
                lambda token: self.executable(token, accessor, *data),
                id=self.task_id()
            ).observe(on_error=self._on_error)

        except Exception as e:
            log.exception(f'[COMMAND] Command {self.name} executed with error {e}')

    def executable(self, token, accessor: ServicesAccessor, *data):
        raise NotImplementedError('Command not implemented')

    def _on_error(self, e):
        log.exception(f'[COMMAND] Command {self.name} executed with error {e}')


class CommandRegistry(metaclass=Singleton):
    _commands: dict[str, Command] = {}

    @classmethod
    def register(cls, command: type[Command]):
        if command.name in cls._commands.keys():
            raise KeyError('Command already exists')
        cls._commands[command.name] = command()

    @classmethod
    def unregister(cls, name: str):
        if name not in cls._commands.keys():
            raise KeyError('Command already exists')
        cls._commands.pop(name)

    @classmethod
    def get(cls, name: str) -> Callable:
        if name not in cls._commands.keys():
            raise KeyError('Command does not exists')
        return cls._commands[name].execute

    @classmethod
    def execute(cls, accessor: ServicesAccessor, name: str, *data):
        cls.get(name)(accessor, *data)
