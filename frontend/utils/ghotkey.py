import ctypes
import ctypes.wintypes
import atexit
import threading
from typing import Callable
from collections import defaultdict


user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_LCONTROL = 0xA2
VK_RCONTROL = 0xA3
VK_MENU = 0x12
VK_LSHIFT = 0xA0
VK_RSHIFT = 0xA1
VK_CAPITAL = 0x14


HOOKPROTYPE = ctypes.CFUNCTYPE(
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_void_p)
)


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", ctypes.wintypes.DWORD),
        ("scanCode", ctypes.wintypes.DWORD),
        ("flags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.wintypes.LPVOID),
    ]


def _uninstallHookProc(hooked):
    if hooked is None:
        return
    user32.UnhookWindowsHookEx(hooked)


def _installHookProc(pointer):
    return user32.SetWindowsHookExA(
        WH_KEYBOARD_LL,
        pointer,
        None,
        0
    )


context = {
    'e': threading.Event(),
    'hotkeys': defaultdict(list),
    'pressed_keys': set()
}


def _hookProc(nCode, wParam, lParam):
    if nCode < 0:
        return user32.CallNextHookEx(context['hook'], nCode, wParam, lParam)
    else:
        if wParam == WM_KEYDOWN or wParam == WM_SYSKEYDOWN:
            keys = set()

            kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            vk = kb.vkCode
            scan = kb.scanCode
            key_state = (ctypes.c_ubyte * 256)()
            user32.GetKeyboardState(ctypes.byref(key_state))
            result = ctypes.c_uint()
            if user32.ToAscii(vk, scan, key_state, ctypes.byref(result), 0):
                keys.add(chr(result.value).upper())

            # Retrieve modifiers
            if (
                user32.GetAsyncKeyState(VK_LSHIFT) & 0x8000
                or user32.GetAsyncKeyState(VK_RSHIFT) & 0x8000
            ):
                keys.add('Shift')
            if (
                user32.GetKeyState(VK_LCONTROL) < 0
                or user32.GetKeyState(VK_RCONTROL) < 0
            ):
                keys.add('Ctrl')
            if user32.GetKeyState(VK_MENU) & 0x8000:
                keys.add('Alt')

            # Avoid auto repeat
            if kb.vkCode not in context['pressed_keys']:
                _callback(keys)
                context['pressed_keys'].add(kb.vkCode)
        elif wParam == WM_KEYUP or wParam == WM_SYSKEYUP:
            kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            if kb.vkCode in context['pressed_keys']:
                context['pressed_keys'].remove(kb.vkCode)

    return user32.CallNextHookEx(context['hook'], nCode, wParam, lParam)


def _callback(keys: set[str]):
    if not keys:
        return

    for shortcut, callbacks in context['hotkeys'].items():
        s_shortcut = set(shortcut.split('+'))
        if s_shortcut.issubset(keys):
            for cb in callbacks:
                cb()


def _install_keyboard_hook_proc():
    context['pointer'] = HOOKPROTYPE(_hookProc)
    hooked = _installHookProc(context['pointer'])
    context['hook'] = hooked
    context['e'].set()
    if hooked:
        msg = ctypes.wintypes.MSG()
        while user32.GetMessageA(ctypes.byref(msg), 0, 0, 0) != 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageA(ctypes.byref(msg))


def install_keyboard_hook_proc():
    th = threading.Thread(target=_install_keyboard_hook_proc)
    th.daemon = True
    th.start()
    context['e'].wait()
    atexit.register(lambda: _uninstallHookProc(context['hook']))
    return bool(context['hook'])


def bind(shortcut: str, callback: Callable):
    context['hotkeys'][shortcut].append(callback)


def unbind(shortcut: str, callback: Callable):
    context['hotkeys'][shortcut].remove(callback)


def unbind_all():
    context['hotkeys'].clear()
