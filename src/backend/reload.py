import subprocess
import sys
import os
import atexit
import time
import socket
import threading
import ctypes
from ctypes import wintypes
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from src.backend.common.utils.logging import log


LOG_TITLE = 'Reloader'

# Env flag marking the spawned worker process so it runs the server directly
# instead of starting yet another supervisor (which would recurse forever).
CHILD_ENV = 'WATCHDOCR_RELOAD_CHILD'

# Debounce window (seconds) to coalesce the burst of events editors emit on a
# single save before triggering a restart.
_RELOAD_DEBOUNCE = 2.0


def is_reload_child() -> bool:
    return os.environ.get(CHILD_ENV) == '1'


_JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000
_JobObjectExtendedLimitInformation = 9


class _JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ('PerProcessUserTimeLimit', wintypes.LARGE_INTEGER),
        ('PerJobUserTimeLimit', wintypes.LARGE_INTEGER),
        ('LimitFlags', wintypes.DWORD),
        ('MinimumWorkingSetSize', ctypes.c_size_t),
        ('MaximumWorkingSetSize', ctypes.c_size_t),
        ('ActiveProcessLimit', wintypes.DWORD),
        ('Affinity', ctypes.c_void_p),
        ('PriorityClass', wintypes.DWORD),
        ('SchedulingClass', wintypes.DWORD),
    ]


class _IO_COUNTERS(ctypes.Structure):
    _fields_ = [(n, ctypes.c_ulonglong) for n in (
        'ReadOperationCount', 'WriteOperationCount', 'OtherOperationCount',
        'ReadTransferCount', 'WriteTransferCount', 'OtherTransferCount',
    )]


class _JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ('BasicLimitInformation', _JOBOBJECT_BASIC_LIMIT_INFORMATION),
        ('IoInfo', _IO_COUNTERS),
        ('ProcessMemoryLimit', ctypes.c_size_t),
        ('JobMemoryLimit', ctypes.c_size_t),
        ('PeakProcessMemoryUsed', ctypes.c_size_t),
        ('PeakJobMemoryUsed', ctypes.c_size_t),
    ]


def _create_kill_on_close_job():
    """Create a Windows job that kills its processes when the handle closes.

    Assigning each spawned worker to this job guarantees the OS terminates it
    when the supervisor exits -- even on a hard kill -- so no orphaned worker
    is left holding the server port. Returns the job handle, or ``None`` if
    job objects are unavailable.
    """
    try:
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        job = kernel32.CreateJobObjectW(None, None)
        if not job:
            return None
        info = _JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        info.BasicLimitInformation.LimitFlags = (
            _JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        )
        ok = kernel32.SetInformationJobObject(
            job,
            _JobObjectExtendedLimitInformation,
            ctypes.byref(info),
            ctypes.sizeof(info),
        )
        if not ok:
            return None
        return job
    except OSError:
        return None


def _assign_to_job(job, proc):
    if job is None:
        return
    try:
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel32.AssignProcessToJobObject(job, int(proc._handle))
    except (OSError, AttributeError):
        pass


def _wait_port_free(host: str, port: int, timeout: float = 10.0) -> bool:
    """Block until ``host:port`` can be bound again, or ``timeout`` elapses.

    After a worker is killed the OS may take a moment to release its listening
    socket; spawning the replacement before then fails to bind (WSA 10048 on
    Windows). Probing with a plain bind (no SO_REUSEADDR) tells us when it is
    truly free.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            probe.bind((host, port))
            return True
        except OSError:
            time.sleep(0.1)
        finally:
            probe.close()
    return False


def serve_with_reload(host: str, port: int):
    """Run a supervisor that (re)spawns the backend worker on source changes.

    The worker is ``python -m src.backend.app`` with ``CHILD_ENV`` set, so the
    child runs the actual server. This process watches ``src/backend`` and
    restarts the child whenever a ``.py`` file changes.
    """
    root = Path(__file__).resolve().parent.parent.parent
    backend_dir = Path(__file__).resolve().parent
    cmd = [
        sys.executable,
        '-m', 'src.backend.app',
        '--host', host,
        '--port', str(port)
    ]
    child_env = {**os.environ, CHILD_ENV: '1'}

    proc_lock = threading.Lock()
    proc_holder = {}

    # Hold the job handle for the supervisor's lifetime; children assigned to
    # it die automatically when this process exits, preventing orphans.
    job = _create_kill_on_close_job()

    def spawn():
        proc = subprocess.Popen(cmd, cwd=root, env=child_env)
        _assign_to_job(job, proc)
        return proc

    def stop_current():
        current = proc_holder.get('proc')
        if current and current.poll() is None:
            current.terminate()
            try:
                current.wait(10)
            except subprocess.TimeoutExpired:
                current.kill()

    log.info('Starting backend server...', extra={'title': LOG_TITLE})
    proc_holder['proc'] = spawn()
    atexit.register(stop_current)

    def restart():
        with proc_lock:
            log.success('Reloading backend server...', extra={'title': LOG_TITLE})
            stop_current()
            if not _wait_port_free(host, port):
                log.warning(
                    'Port %s:%s still busy after timeout, spawning anyway',
                    host, port,
                    extra={'title': LOG_TITLE}
                )
            proc_holder['proc'] = spawn()

    reloader = _BackendReloader(restart)
    observer = Observer()
    observer.schedule(reloader, str(backend_dir), recursive=True)
    observer.daemon = True
    observer.start()
    atexit.register(observer.stop)

    log.info(
        'Auto-reload enabled, watching %s',
        backend_dir,
        extra={'title': LOG_TITLE}
    )

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        log.info('Shutting down...', extra={'title': LOG_TITLE})


class _BackendReloader(FileSystemEventHandler):
    """Restarts the backend process when a Python source file changes.

    Watchdog delivers events from its own thread and editors emit several
    events per save, so changes are debounced onto a single timer before the
    restart callback fires.
    """

    def __init__(self, restart):
        self._restart = restart
        self._timer = None
        self._lock = threading.Lock()

    def on_any_event(self, event: FileSystemEvent):
        if event.is_directory:
            return
        src_path = str(event.src_path)
        if not src_path.endswith('.py'):
            return
        if '__pycache__' in src_path:
            return
        log.info(
            'Change detected: %s (%s)',
            src_path,
            event.event_type,
            extra={'title': LOG_TITLE}
        )
        self._schedule_restart()

    def _schedule_restart(self):
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(_RELOAD_DEBOUNCE, self._restart)
            self._timer.daemon = True
            self._timer.start()
