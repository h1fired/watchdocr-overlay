import subprocess
import sys
import atexit
from pathlib import Path


def run_server(host: str, port: int):
    root = Path(__file__).resolve().parent.parent.parent
    cmd = [
        sys.executable,
        '-m', 'src.backend.app',
        '--host', host,
        '--port', str(port)
    ]
    proc = subprocess.Popen(cmd, cwd=root)

    atexit.register(lambda: (proc.terminate(), proc.wait(10)))
