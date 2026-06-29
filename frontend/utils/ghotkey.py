from typing import Callable
from collections import defaultdict
from ctypes import wintypes
import ctypes
import atexit
import threading
import queue


user32 = ctypes.windll.user32


WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104
WM_KEYUP = 0x0101
WM_SYSKEYUP = 0x0105

VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12


HOOKPROTYPE = ctypes.CFUNCTYPE(
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p)
)


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", wintypes.LPVOID),
    ]


context = {
    'e': threading.Event(),
    'hotkeys': defaultdict(list),
    'pressed_keys': set(),
    'hook': None,
    'running': True
}
event_queue = queue.Queue()


def _process_callbacks():
    while context['running']:
        try:
            # Wait for keystrokes from the hook
            keys = event_queue.get(timeout=0.5)
            if not keys:
                continue

            for shortcut, callbacks in context['hotkeys'].items():
                s_shortcut = set(shortcut.split('+'))
                if s_shortcut.issubset(keys):
                    for cb in callbacks:
                        cb()
        except queue.Empty:
            continue


def _hookProc(nCode, wParam, lParam):
    if nCode >= 0:
        kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
        vk = kb.vkCode

        if wParam in (WM_KEYDOWN, WM_SYSKEYDOWN):
            if vk not in context['pressed_keys']:
                context['pressed_keys'].add(vk)

                keys = set()

                char_code = user32.MapVirtualKeyA(vk, 2)
                if char_code:
                    keys.add(chr(char_code & 0xFF).upper())

                # Use GetAsyncKeyState for true asynchronous hardware state
                if user32.GetAsyncKeyState(VK_SHIFT) & 0x8000:
                    keys.add('Shift')
                if user32.GetAsyncKeyState(VK_CONTROL) & 0x8000:
                    keys.add('Ctrl')
                if user32.GetAsyncKeyState(VK_MENU) & 0x8000:
                    keys.add('Alt')

                # Offload to the queue immediately. Do NOT run callbacks here.
                event_queue.put(keys)

        elif wParam in (WM_KEYUP, WM_SYSKEYUP):
            if vk in context['pressed_keys']:
                context['pressed_keys'].remove(vk)

    return user32.CallNextHookEx(context['hook'], nCode, wParam, lParam)


def _install_keyboard_hook_proc():
    context['pointer'] = HOOKPROTYPE(_hookProc)
    context['hook'] = user32.SetWindowsHookExA(WH_KEYBOARD_LL, context['pointer'], None, 0)

    context['e'].set()

    if context['hook']:
        msg = wintypes.MSG()
        # Windows requires a message pump to keep the hook alive
        while user32.GetMessageA(ctypes.byref(msg), 0, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageA(ctypes.byref(msg))


def _uninstallHookProc():
    context['running'] = False
    if context['hook']:
        user32.UnhookWindowsHookEx(context['hook'])


def install_keyboard_hook_proc():
    processor_thread = threading.Thread(target=_process_callbacks, daemon=True)
    processor_thread.start()

    th = threading.Thread(target=_install_keyboard_hook_proc, daemon=True)
    th.start()

    context['e'].wait()
    atexit.register(_uninstallHookProc)
    return bool(context['hook'])


def bind(shortcut: str, callback: Callable):
    context['hotkeys'][shortcut].append(callback)


def unbind(shortcut: str, callback: Callable):
    if callback in context['hotkeys'][shortcut]:
        context['hotkeys'][shortcut].remove(callback)


def unbind_all():
    context['hotkeys'].clear()
