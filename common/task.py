import time
import queue
import heapq
import inspect
from typing import Callable, TypeAlias, Any
from enum import Enum

from common.utils.logger import log
from common.observable import MappedObservable

from threading import Thread, Event, Condition


class CancelationError(Exception):
    pass


class CancelationToken:
    def __init__(self):
        self._is_cancelled = False

    def cancel(self):
        if self._is_cancelled:
            raise CancelationError('Token was cancelled')
        self._is_cancelled = True

    @property
    def is_cancelled(self):
        return self._is_cancelled

    def exceptional_check(self):
        if self._is_cancelled:
            raise CancelationError('Token was cancelled')


# Period
class Period:
    def __init__(self, interval: float, repeats=-1):
        if repeats < -1:
            raise ValueError('Invalid repeats value (should be greater than or equals -1)')
        if interval < 0:
            raise ValueError('Invalid interval value (should be positive)')

        self._interval = interval
        self._repeats = repeats
        self._timestamp = 0.
        self._times = 0
        self._finished = False

    def execution_time(self):
        return self._timestamp + self._interval

    def next(self):
        if self._times >= self._repeats and self._repeats != -1:
            raise RuntimeError('Repetition limit reached')
        self._times += 1
        self._timestamp = time.monotonic()

    def is_done(self):
        if self._finished:
            return True
        if self._repeats == -1:
            return False
        return self._times >= self._repeats

    def renew_time(self):
        self._timestamp = time.monotonic()

    def finish(self):
        self._finished = True

    @property
    def repeats(self):
        return self._repeats

    @property
    def times(self):
        return self._times


# Environment
NUM_WORKERS = 64


class EnvironmentType(str, Enum):
    THREAD = 'thread'


class Environment:
    def __init__(self):
        pass

    def push(self, executable: Callable):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError

    def shutdown(self):
        raise NotImplementedError


# Environment / threading
class ThreadPool:
    def __init__(self):
        self._workers: list[Thread] = []
        self._stop_event = Event()
        self._q_waiter = Condition()
        self._q = queue.Queue()

    def run(self):
        self._stop_event.clear()
        for _ in range(NUM_WORKERS):
            thread = Thread(target=self._worker, daemon=True)
            thread.daemon = True
            thread.start()
            self._workers.append(thread)

    def stop(self):
        self._stop_event.set()
        self._q.queue.clear()
        with self._q_waiter:
            self._q_waiter.notify_all()
        for worker in self._workers:
            worker.join()

    def push(self, executable: Callable):
        self._q.put(executable)
        with self._q_waiter:
            self._q_waiter.notify_all()

    def _worker(self):
        while not self._stop_event.is_set():
            try:
                task = self._q.get_nowait()
                task()
                self._q.task_done()
            except queue.Empty:
                pass
            with self._q_waiter:
                self._q_waiter.wait()


class ThreadingEnvironment(Environment):
    def __init__(self):
        super().__init__()
        self._pool = ThreadPool()

    def push(self, executable: Callable):
        self._pool.push(executable)

    def run(self):
        self._pool.run()

    def shutdown(self):
        self._pool.stop()


# Task
TaskType: TypeAlias = 'Task | Callable[..., Any] | Pipeline'


class Task:
    def __init__(self):
        self._e = Event()

    def executable(self, token: CancelationToken):
        raise NotImplementedError

    def sleep(self, seconds: float):
        self._e.wait(seconds)

    def dispose(self):
        self._e.set()


class TaskDefinition:
    def __init__(self, period: Period, environment: Environment):
        self._period = period
        self._env = environment

    @property
    def period(self):
        return self._period

    @property
    def environment(self):
        return self._env


class TaskCollection:
    def __init__(self):
        self._tasks: dict[str, _TaskWrapper] = {}
        self._anonymous_tasks: list[_TaskWrapper] = []

    def add(self, task: '_TaskWrapper'):
        if task.id() is None:
            self._anonymous_tasks.append(task)
        else:
            if task.id() in self._tasks.keys():
                raise KeyError(f'Task with ID={task.id()} already exists')
            self._tasks[task.id()] = task

    def get(self, id: str):
        return self._tasks[id]

    def remove(self, task: '_TaskWrapper'):
        if task.id() in self._tasks:
            self._tasks.pop(task.id())
        else:
            self._anonymous_tasks.remove(task)

    def all(self) -> list['_TaskWrapper']:
        return list(self._tasks.values()) + self._anonymous_tasks

    def exists(self, id: str):
        return id in self._tasks.keys()

    def count(self):
        return len(self._tasks) + len(self._anonymous_tasks)


# Wrapper
class _TaskWrapperSignal(str, Enum):
    RESULT = 'R'
    ERROR = 'E'
    FINISH = 'F'


class _TaskWrapper:
    def __init__(
        self,
        task: TaskType,
        definition: TaskDefinition,
        token: CancelationToken,
        id: str | None = None
    ):
        self._task = task
        self._definition = definition
        self._token = token
        self._id = id

        self._observer = MappedObservable()
        self._dsignal = Event()
        self._psignal = None

        self._result = None
        self._finished = False
        self._executing = False

    def execute(self):
        if self._finished or self._executing:
            raise RuntimeError('Task already finished or executing')

        if not self._token.is_cancelled:
            self._executing = True

            self._dsignal.clear()

            try:
                self.executable(self._task, self._token, self._observer)
            except Exception as e:
                log.error(e, extra={'title': 'TASK'})
                self._observer.notify(_TaskWrapperSignal.ERROR.value, e)

            self._executing = False
        else:
            self._definition.period.finish()

        if self._definition.period.is_done():
            self._finished = True
            if self._psignal:
                self._psignal(self)
            self._observer.notify(_TaskWrapperSignal.FINISH.value)
            self._dsignal.set()

    def executable(
        self,
        task: TaskType,
        token: CancelationToken,
        signal: MappedObservable
    ):
        raise NotImplementedError

    def id(self):
        return self._id

    def definition(self):
        return self._definition

    def wait(self):
        self._dsignal.wait()

    def cancel(self):
        self._token.cancel()

    def signal(self, signal: _TaskWrapperSignal, handler: Callable):
        self._observer.register(signal.value, handler)

    def result(self):
        return self._result

    def finished(self):
        return self._finished

    def executing(self):
        return self._executing

    def cancelled(self):
        return self._token.is_cancelled

    def __lt__(self, other: '_TaskWrapper'):
        return (
            self._definition.period.execution_time()
            < other._definition.period.execution_time()
        )

    def __gt__(self, other: '_TaskWrapper'):
        return (
            self._definition.period.execution_time()
            > other._definition.period.execution_time()
        )

    def __eq__(self, other: '_TaskWrapper'):
        return (
            self._definition.period.execution_time()
            == other._definition.period.execution_time()
        )


class _SimpleTaskWrapper(_TaskWrapper):
    def __init__(self, task, definition, token, id=None):
        super().__init__(task, definition, token, id)
        self._waiter = None

    def executable(self, task, token, signal):
        if isinstance(task, Task):
            self._waiter = task._e
            task_func = task.executable
        else:
            task_func = task
        result = task_func(token)
        signal.notify(_TaskWrapperSignal.RESULT, result)

    def cancel(self):
        super().cancel()
        if self._waiter:
            self._waiter.set()


# Pipeline
class Pipeline:
    def __init__(self):
        stages = {}
        for name, func in inspect.getmembers(self, predicate=inspect.ismethod):
            if name.startswith('stage'):
                index = int(name[-1])
                if index in stages:
                    raise ValueError('Bad stages names')
                stages[index] = func

        indexes = sorted(stages.keys())
        if len(indexes) > 1 and all(indexes[i] + 1 != indexes[i + 1] for i in range(len(indexes) - 1)):
            raise ValueError('Bad stages names')
        self._stages = stages

    def process(self, data=None):
        for stage in self._stages.values():
            data = stage(data)
            yield data


class _PipelineTaskWrapper(_TaskWrapper):
    def executable(self, task, token, signal):
        for i, data in enumerate(task.process()):
            signal.notify(_TaskWrapperSignal.RESULT, i+1, data)


# Future
class Future:
    def __init__(self, task: _TaskWrapper):
        self._task = task

    def wait(self):
        self._task.wait()

    def cancel(self):
        self._task.cancel()

    def result(self):
        return self._task.result()

    def finished(self):
        return self._task.finished()

    def observe(
        self,
        on_finish: Callable | None = None,
        on_error: Callable | None = None,
        on_result: Callable | None = None
    ):
        if on_finish:
            self._task.signal(_TaskWrapperSignal.FINISH, on_finish)
        if on_error:
            self._task.signal(_TaskWrapperSignal.ERROR, on_error)
        if on_result:
            self._task.signal(_TaskWrapperSignal.RESULT, on_result)
        return self


# Scheduler
class Scheduler:
    def __init__(self, callback: Callable):
        self._heap: list[_TaskWrapper] = []
        self._th = None
        self._cb = callback
        self._stop_event = Event()
        self._waiter = Condition()

    def run(self):
        self._stop_event.clear()

        self._th = Thread(target=self._worker, daemon=True)
        self._th.start()

    def shutdown(self):
        self._stop_event.set()

        with self._waiter:
            self._waiter.notify_all()
        if self._th and self._th.is_alive():
            self._th.join()

    def push(self, task: _TaskWrapper):
        heapq.heappush(self._heap, task)
        with self._waiter:
            self._waiter.notify_all()

    def _worker(self):
        while not self._stop_event.is_set():
            next_sleep_time = None

            # Wait for incoming tasks if heap is empty
            if not self._heap:
                with self._waiter:
                    self._waiter.wait(next_sleep_time)
                continue

            task = self._heap[0]

            # Schedule task by period execution time
            now = time.monotonic()
            definition = task.definition()
            if definition.period.execution_time() <= now:
                heapq.heappop(self._heap)

                if not definition.period.is_done():
                    # Renew execution time (now time + task interval)
                    # if task is executing, else update. Thats prevent
                    # asyncronous tasks calling (when task execution
                    # time bigger than period execution time)
                    if task.executing():
                        definition.period.renew_time()
                    else:
                        definition.period.next()
                if not definition.period.is_done() and not task.cancelled():
                    heapq.heappush(self._heap, task)
                self._cb(task)  # Push task to callback
                continue
            else:
                # Calculate next sleep time
                next_sleep_time = definition.period.execution_time() - now

            with self._waiter:
                self._waiter.wait(next_sleep_time)


# Manager
class _TaskManagerModel:
    def __init__(self):
        self._model = TaskCollection()
        self._environments: dict[EnvironmentType, Environment] = {
            EnvironmentType.THREAD: ThreadingEnvironment()
        }
        self._scheduler = Scheduler(self.on_scheduler_task)
        self._running = False

    def run(self):
        if self._running:
            raise RuntimeError('Task manager already started')

        for env in self._environments.values():
            env.run()
        self._scheduler.run()

        self._running = True

    def shutdown(self):
        if not self._running:
            raise RuntimeError('Task manager already terminated')

        for task in self._model.all():
            if not task.cancelled():
                task.cancel()
        for task in self._model.all():
            task.wait()
        for env in self._environments.values():
            env.shutdown()
        self._scheduler.shutdown()

        self._running = False

    def is_running(self):
        return self._running

    def execute(
        self,
        task: TaskType,
        period: Period,
        environment: EnvironmentType,
        id: str | None = None
    ):
        if not self._running:
            raise RuntimeError('Task manager is not alive')

        token = CancelationToken()
        definition = TaskDefinition(period, environment)

        if isinstance(task, (Task, Callable)):
            wrapper = _SimpleTaskWrapper(task, definition, token, id)
        else:
            wrapper = _PipelineTaskWrapper(task, definition, token, id)

        wrapper._psignal = self.on_finish_task

        self._model.add(wrapper)
        self._scheduler.push(wrapper)

        return Future(wrapper)

    def objects(self):
        return self._model

    # Handlers
    def on_scheduler_task(self, task: _TaskWrapper):
        env = self._environments[task.definition().environment]
        env.push(task.execute)

    def on_finish_task(self, task: _TaskWrapper):
        self._model.remove(task)


class TaskManager:
    Signal = _TaskWrapperSignal

    _model = _TaskManagerModel()

    @classmethod
    def run(cls):
        cls._model.run()

    @classmethod
    def shutdown(cls):
        cls._model.shutdown()

    @classmethod
    def is_running(self):
        return self._model.is_running()

    @classmethod
    def execute(
        cls,
        task: TaskType,
        period: Period = Period(0, 1),
        environment: EnvironmentType = EnvironmentType.THREAD,
        id: str | None = None
    ):
        return cls._model.execute(task, period, environment, id)

    @classmethod
    def objects(cls):
        return cls._model.objects()
