from frontend.core import GuiCoreApplication
from frontend.utils import ghotkey
from frontend.preloader.preloader import PreloaderCore
from src.core import WatchdOcrCore
from src.utils.sysbehavior import SingleInstance
from src.common.utils.logging import log
from config import config
import subprocess
import sys
import ctypes
import argparse
import asyncio


ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('company.app.1')


SHUTDOWN_TIMEOUT = 3


def show_overlay():
    gui = GuiCoreApplication()
    gui.system_obj().setVisible(True)


async def shutdown(core: WatchdOcrCore):
    try:
        async with asyncio.timeout(SHUTDOWN_TIMEOUT):
            await core.destroy()
    except TimeoutError:
        log.warning(
            'Core shutdown timed out after %ss. Forcing exit...',
            SHUTDOWN_TIMEOUT,
            extra={'title': 'Core'}
        )
    except Exception:
        log.exception('Core shutdown failed', extra={'title': 'Core'})

    ghotkey.uninstall_keyboard_hook_proc()
    GuiCoreApplication().destroy()


async def main(args: argparse.Namespace):
    gui = GuiCoreApplication()

    # Check for single application instance
    guard = SingleInstance(config.APP_ID)
    if not guard.try_run():
        return 0

    guard.activate_requested.connect(show_overlay)

    core = WatchdOcrCore()
    try:
        await core.initialize()

        # Run preloader
        preloader = PreloaderCore(core.plugins_manager())
        if not await preloader.exec():
            return 0

        gui.tray().setShowActiveVisible(True)

        # Load GUI core
        gui.load(core.api_collection(), core.event_system())

        # Install global keyboard events hook
        await ghotkey.install_keyboard_hook_proc()

        sys_obj = gui.system_obj()
        if not args.hide_on_exec:
            sys_obj.setVisible(True)
        else:
            sys_obj.setWindowTransparentForInput(True)

        await gui.wait_for_quit()
    finally:
        await shutdown(core)

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=config.APP_NAME)
    parser.add_argument('--hide-on-exec', action='store_true')
    args = parser.parse_args()

    if config.DEBUG:
        cmd = ' '.join((
            sys.executable,
            '-B ./tools/resources.py',
            '--generate',
            '--compile'
        ))
        subprocess.run(cmd, check=True)

        from frontend import qresources as _res
        _res.qInitResources()
    else:
        try:
            from frontend import qresources as _res
            _res.qInitResources()
        except ImportError as e:
            raise ImportError(
                'Resources modules not found. Maybe '
                'you forgot to compile the resource files?'
            ) from e

    gui = GuiCoreApplication()
    gui.pre_init()

    sys.exit(gui.exec(main(args)))
