from qt.core import QObject, Slot
from qt.gui import QWindow
import ctypes


user32 = ctypes.windll.user32


class FocusHelper(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._previous_hwnd = None

    @Slot(QWindow)
    def grab_focus(self, window):
        self._previous_hwnd = user32.GetForegroundWindow()
        hwnd = int(window.winId())
        # Allow our process to set foreground window
        current_thread = ctypes.windll.kernel32.GetCurrentThreadId()
        fg_thread = user32.GetWindowThreadProcessId(self._previous_hwnd, None)
        user32.AttachThreadInput(fg_thread, current_thread, True)
        user32.SetForegroundWindow(hwnd)
        user32.AttachThreadInput(fg_thread, current_thread, False)

    @Slot()
    def restore_focus(self):
        if self._previous_hwnd:
            user32.SetForegroundWindow(self._previous_hwnd)
            self._previous_hwnd = None
