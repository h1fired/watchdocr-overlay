from typing import Callable, Any, TypeAlias
from threading import Thread, Event, Lock, Condition
from enum import Enum
import queue
import time
import heapq
from .observer import MappedObserver
from .utils.meta import Singleton
from .utils.logger import log


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


class Task:
    def __init__(self):
        self._waiter = Event()

    def executable(self, token: CancelationToken):
        raise NotImplementedError

    def sleep(self, seconds: float):
        self._waiter.wait(seconds)


TaskType: TypeAlias = 'Task | Callable[..., Any]'


# Environment
class TaskEnvironment(str, Enum):
    THREAD = 'thread'


class _Environment:
    def __init__(self):
        pass

    def push(self, executable: Callable):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError

    def shutdown(self):
        raise NotImplementedError


# Threading
NUM_WORKERS = 64


class ThreadPool:
    def __init__(self):
        self._workers: list[Thread] = []
        self._stop_event = Event()
        self._q = queue.Queue()

    def run(self):
        self._stop_event.clear()
        for _ in range(NUM_WORKERS):
            thread = Thread(target=self._worker)
            thread.daemon = True
            thread.start()
            self._workers.append(thread)

    def stop(self):
        self._stop_event.set()
        self._q.queue.clear()
        for worker in self._workers:
            worker.join()

    def push(self, executable: Callable):
        self._q.put(executable)

    def _worker(self):
        while not self._stop_event.is_set():
            try:
                task = self._q.get(timeout=0.1)
                task()
                self._q.task_done()
            except queue.Empty:
                pass


class _ThreadingEnvironment(_Environment):
    def __init__(self):
        super().__init__()
        self._pool = ThreadPool()

    def push(self, executable: Callable):
        self._pool.push(executable)

    def run(self):
        self._pool.run()

    def shutdown(self):
        self._pool.stop()


# Scheduler
class Period:
    def __init__(self, interval: float, repeats=-1, async_repeat=False):
        self._interval = interval
        self._repeats = repeats
        self._timestamp = 0.
        self._times = 1
        self._async_repeat = async_repeat

    def execution_time(self):
        return self._timestamp + self._interval

    def next(self):
        self._times += 1
        if self._times > self._repeats and self._repeats != -1:
            raise RuntimeError('Repetition limit reached')
        self._timestamp = time.time()

    def is_done(self):
        if self._repeats == -1:
            return False
        return self._times >= self._repeats

    def is_async(self):
        return self._async_repeat


class Scheduler:
    def __init__(self, execution_callback: Callable):
        self._cb = execution_callback
        self._heap: list[_TaskWrapper] = []
        self._stop_event = Event()
        self._th = None
        self._waiter = Condition()
        self._lock = Lock()

    def run(self, run_in_background=False):
        self._stop_event.clear()
        with self._waiter:
            self._waiter.notify_all()
        if run_in_background:
            self._th = Thread(target=self._worker, daemon=True)
            self._th.start()

    def shutdown(self):
        self._stop_event.set()
        with self._waiter:
            self._waiter.notify_all()
        if self._th and self._th.is_alive():
            self._th.join()

    def schedule(self, task: '_TaskWrapper'):
        heapq.heappush(self._heap, task)
        with self._waiter:
            self._waiter.notify_all()

    def _worker(self):
        while not self._stop_event.is_set():
            next_sleep = 0.1
            if self._heap:
                task = self._heap[0]
                if not task.period.is_async() and task.executing():
                    with self._waiter:
                        self._waiter.wait(next_sleep)
                    continue
                now = time.time()
                if task.period.execution_time() <= now:
                    heapq.heappop(self._heap)
                    self._cb(task)
                    if not task.period.is_done() and not task.is_cancelled():
                        heapq.heappush(self._heap, task)
                        task.period.next()
                    else:
                        task.set_last_execution()
                    continue
                else:
                    next_sleep = task.period.execution_time() - now
            with self._waiter:
                self._waiter.wait(next_sleep)


# Manager
class _TaskWrapper:
    def __init__(
        self,
        task: TaskType,
        period: 'Period',
        environment=TaskEnvironment.THREAD,
        token: CancelationToken | None = None,
        id: str = None
    ):
        if isinstance(task, Task):
            self._task = task.executable
            self._waiter = task._waiter
        else:
            self._task = task
        self._period = period
        self._env = environment
        self._token = token
        self._id = id
        self._finish_event = Event()
        self._signal_obs = MappedObserver()
        self._result = None
        self._is_executing = False
        self._last_execution = False

    def execute(self):
        self._is_executing = True
        self._finish_event.clear()
        try:
            result = self._task(self._token)
            self._result = result
            self._signal_obs.notify('RESULT', result)
        except Exception as e:
            self._signal_obs.notify('ERROR', e)
            log.error(f'[TASK] {e}')
        self._is_executing = False
        if self._last_execution:
            self._finish_event.set()
            self._signal_obs.notify('FINISH')

    def executing(self):
        return self._is_executing

    def cancel(self):
        self._token.cancel()
        if hasattr(self, '_waiter'):
            self._waiter.set()

    def wait(self):
        self._finish_event.wait()

    def set_last_execution(self):
        self._last_execution = True

    def result(self):
        return self._result

    def is_cancelled(self):
        return self._token.is_cancelled

    @property
    def id(self):
        return self._id

    @property
    def period(self):
        return self._period

    @property
    def env(self):
        return self._env

    def signal(self, type: str, handler: Callable):
        self._signal_obs.register(type, handler)

    def __lt__(self, other: '_TaskWrapper'):
        return self._period.execution_time() < other.period.execution_time()

    def __gt__(self, other: '_TaskWrapper'):
        return self._period.execution_time() > other.period.execution_time()

    def __eq__(self, other: '_TaskWrapper'):
        return self._period.execution_time() == other.period.execution_time()


class Future:
    def __init__(self, task: _TaskWrapper):
        self._task = task

    def wait(self):
        self._task.wait()

    def cancel(self):
        self._task.cancel()

    def result(self):
        return self._task.result()

    def observe(
        self,
        on_finish: Callable | None = None,
        on_error: Callable | None = None,
        on_result: Callable | None = None
    ):
        if on_finish:
            self._task.signal('FINISH', on_finish)
        if on_error:
            self._task.signal('ERROR', on_error)
        if on_result:
            self._task.signal('RESULT', on_result)
        return self


class TaskCollection:
    def __init__(self):
        self._tasks: dict[str, _TaskWrapper] = {}
        self._anonymous_tasks: list[_TaskWrapper] = []

    def add(self, task: _TaskWrapper):
        if task.id is None:
            self._anonymous_tasks.append(task)
        else:
            if task.id in self._tasks.keys():
                raise KeyError(f'Task with ID={task.id} already exists')
            self._tasks[task.id] = task

    def get(self, id: str):
        return self._tasks[id]

    def remove(self, task: _TaskWrapper):
        if task.id in self._tasks:
            self._tasks.pop(task.id)
        else:
            self._anonymous_tasks.remove(task)

    def all(self) -> list[_TaskWrapper]:
        return list(self._tasks.values()) + self._anonymous_tasks

    def exists(self, id: str):
        return id in self._tasks.keys()

    def count(self):
        return len(self._tasks) + len(self._anonymous_tasks)

    def clear(self):
        self._tasks.clear()
        self._anonymous_tasks.clear()


class TaskManager(metaclass=Singleton):
    def __init__(self):
        self._environments: dict[TaskEnvironment, _Environment] = {
            TaskEnvironment.THREAD: _ThreadingEnvironment(),
        }
        self._scheduler = Scheduler(self.on_scheduler_task)
        self._is_running = False
        self._tasks = TaskCollection()

    def run(self):
        if self._is_running:
            raise RuntimeError('Task manager already started')
        self._scheduler.run(run_in_background=True)
        for env in self._environments.values():
            env.run()
        self._is_running = True

    def shutdown(self):
        if not self._is_running:
            raise RuntimeError('Task manager already terminated')
        for task in self._tasks.all():
            task.cancel()
        for env in self._environments.values():
            env.shutdown()
        self._scheduler.shutdown()
        self._tasks.clear()
        self._is_running = False

    def is_running(self):
        return self._is_running

    def execute(
        self,
        task: TaskType,
        period: Period = Period(0, 1),
        environment=TaskEnvironment.THREAD,
        id: str = None
    ):
        if not self._is_running:
            raise RuntimeError('Task manager is not alive')
        token = CancelationToken()
        w_task = _TaskWrapper(task, period, environment, token, id)
        w_task.signal('FINISH', lambda: self.on_remove_task(w_task))
        self._tasks.add(w_task)
        self._scheduler.schedule(w_task)
        return Future(w_task)

    def cancel_task(self, id: str):
        task = self._tasks.get(id)
        task.cancel()

    def wait_for_task(self, id: str):
        try:
            task = self._tasks.get(id)
            task.wait()
        except KeyError:
            log.warning('[TASK] Task not found - quiet waiting')

    def exists(self, id: str):
        return self._tasks.exists(id)

    def count(self):
        return self._tasks.count()

    def observe(
        self,
        id: str,
        on_finish: Callable | None = None,
        on_error: Callable | None = None,
        on_result: Callable | None = None
    ):
        task = self._tasks.get(id)
        if on_finish:
            task.signal('FINISH', on_finish)
        if on_error:
            task.signal('ERROR', on_error)
        if on_result:
            task.signal('RESULT', on_result)
        return self

    def on_scheduler_task(self, task: _TaskWrapper):
        env = self._environments[task.env]
        env.push(task.execute)

    def on_remove_task(self, task: _TaskWrapper):
        self._tasks.remove(task)
