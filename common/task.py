import time
import queue
import heapq
from typing import Callable, TypeAlias, Any
from enum import Enum

from common.utils.logger import log
from common.observable import MappedObservable, ObservableVar

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
TaskType: TypeAlias = 'Task | Callable[..., Any]'


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
        self._tasks: dict[str, _Task] = {}
        self._anonymous_tasks: list[_Task] = []

    def add(self, task: '_Task'):
        if task.id() is None:
            self._anonymous_tasks.append(task)
        else:
            if task.id() in self._tasks.keys():
                raise KeyError(f'Task with ID={task.id()} already exists')
            self._tasks[task.id()] = task

    def get(self, id: str):
        return self._tasks[id]

    def remove(self, task: '_Task'):
        if task.id() in self._tasks:
            self._tasks.pop(task.id())
        else:
            self._anonymous_tasks.remove(task)

    def all(self) -> list['_Task']:
        return list(self._tasks.values()) + self._anonymous_tasks

    def exists(self, id: str):
        return id in self._tasks.keys()

    def count(self):
        return len(self._tasks) + len(self._anonymous_tasks)


class TaskSignal(str, Enum):
    RESULT = 'R'
    ERROR = 'E'
    FINISH = 'F'


class _Task:
    def __init__(
        self,
        task: TaskType,
        definition: TaskDefinition,
        token: CancelationToken,
        id: str | None = None
    ):
        if isinstance(task, Task):
            self._task = task.executable
            self._waiter = task._e
        else:
            self._task = task

        self._definition = definition
        self._id = id
        self._token = token

        self._dsignal = Event()
        self._psignal = None

        self._observer = MappedObservable()

        self._result = None
        self._finished = False
        self._executing = False

    def id(self):
        return self._id

    def definition(self):
        return self._definition

    def execute(self):
        if self._finished or self._executing:
            raise RuntimeError('Task already finished or executing')

        if not self._token.is_cancelled:
            self._executing = True

            self._dsignal.clear()

            try:
                result = self._task(self._token)
                self._result = result
                self._observer.notify(TaskSignal.RESULT.value, result)
            except Exception as e:
                log.error(e, extra={'title': 'TASK'})
                self._observer.notify(TaskSignal.ERROR.value, e)

            self._executing = False
        else:
            self._definition.period.finish()

        if self._definition.period.is_done():
            self._finished = True
            if self._psignal:
                self._psignal(self)
            self._observer.notify(TaskSignal.FINISH.value)
            self._dsignal.set()

    def wait(self):
        self._dsignal.wait()

    def cancel(self):
        self._token.cancel()
        if hasattr(self, '_waiter'):
            self._waiter.set()

    def signal(self, signal: TaskSignal, handler: Callable):
        self._observer.register(signal.value, handler)

    def result(self):
        return self._result

    def finished(self):
        return self._finished

    def executing(self):
        return self._executing

    def cancelled(self):
        return self._token.is_cancelled

    def __lt__(self, other: '_Task'):
        return (
            self._definition.period.execution_time()
            < other._definition.period.execution_time()
        )

    def __gt__(self, other: '_Task'):
        return (
            self._definition.period.execution_time()
            > other._definition.period.execution_time()
        )

    def __eq__(self, other: '_Task'):
        return (
            self._definition.period.execution_time()
            == other._definition.period.execution_time()
        )


class Future:
    def __init__(self, task: _Task):
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
            self._task.signal(TaskSignal.FINISH, on_finish)
        if on_error:
            self._task.signal(TaskSignal.ERROR, on_error)
        if on_result:
            self._task.signal(TaskSignal.RESULT, on_result)
        return self


# Scheduler
class Scheduler:
    def __init__(self, callback: Callable):
        self._heap: list[_Task] = []
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

    def push(self, task: _Task):
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


# Pipeline
class Stage:
    def __init__(self):
        pass

    def process(self, *data):
        raise NotImplementedError


class Pipeline:
    def __init__(self, *stages: Stage | Callable):
        self._stages = stages
        self._current_stage = ObservableVar(int, 0)
        self._future: Future = None

    def start(self, token: CancelationToken, data=None):
        for i, stage in enumerate(self._stages):
            if token.is_cancelled:
                return data
            if type(stage) is Stage:
                data = stage.process(token, data)
            else:
                data = stage(token, data)
            self._current_stage.value = i
        return data

    @property
    def current_stage(self):
        return self._current_stage

    def future(self):
        return self._future


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
        wrapper = _Task(task, definition, token, id)
        wrapper._psignal = self.on_finish_task

        self._model.add(wrapper)
        self._scheduler.push(wrapper)

        return Future(wrapper)

    def execute_pipeline(
        self,
        *stages: Stage | Callable,
        environment: EnvironmentType = EnvironmentType.THREAD,
        id: str | None = None
    ):
        pipeline = Pipeline(*stages)
        future = self.execute(
            task=pipeline.start,
            period=Period(0, 1),
            environment=environment,
            id=id
        )
        pipeline._future = future
        return pipeline

    def objects(self):
        return self._model

    # Handlers
    def on_scheduler_task(self, task: _Task):
        env = self._environments[task.definition().environment]
        env.push(task.execute)

    def on_finish_task(self, task: _Task):
        self._model.remove(task)


class TaskManager:
    Signal = TaskSignal

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
    def execute_pipeline(
        cls,
        *stages: Stage | Callable,
        environment: EnvironmentType = EnvironmentType.THREAD,
        id: str | None = None
    ):
        return cls._model.execute_pipeline(
            *stages,
            environment=environment,
            id=id
        )

    @classmethod
    def objects(cls):
        return cls._model.objects()
