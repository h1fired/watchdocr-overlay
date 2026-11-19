from src.common.utils.logging import log
from typing import Callable
from collections import defaultdict
from ctypes import wintypes
import ctypes
import asyncio
import threading


user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


WH_KEYBOARD_LL = 13
WM_QUIT = 0x0012
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104
WM_KEYUP = 0x0101
WM_SYSKEYUP = 0x0105
PM_NOREMOVE = 0x0000

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
    'hotkeys': defaultdict(list),
    'pressed_keys': set(),
    'hook': None,
    'thread_id': None,
    'loop': None
}


def _process_keys(keys: set):
    # Executed in the event loop thread
    for shortcut, callbacks in tuple(context['hotkeys'].items()):
        s_shortcut = set(shortcut.split('+'))
        if s_shortcut.issubset(keys):
            for cb in tuple(callbacks):
                try:
                    cb()
                except Exception:
                    log.exception(
                        'Hotkey %s callback failed', shortcut,
                        extra={'title': 'Hotkeys'}
                    )


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

                # Offload to the event loop immediately. Do NOT run callbacks here.
                try:
                    context['loop'].call_soon_threadsafe(_process_keys, keys)
                except RuntimeError:
                    pass  # Event loop is closed

        elif wParam in (WM_KEYUP, WM_SYSKEYUP):
            if vk in context['pressed_keys']:
                context['pressed_keys'].remove(vk)

    return user32.CallNextHookEx(context['hook'], nCode, wParam, lParam)


def _install_keyboard_hook_proc(installed: asyncio.Future):
    loop = context['loop']

    context['pointer'] = HOOKPROTYPE(_hookProc)
    context['hook'] = user32.SetWindowsHookExA(WH_KEYBOARD_LL, context['pointer'], None, 0)
    context['thread_id'] = kernel32.GetCurrentThreadId()

    # Force message queue creation, so WM_QUIT can be posted to this thread
    msg = wintypes.MSG()
    user32.PeekMessageA(ctypes.byref(msg), 0, 0, 0, PM_NOREMOVE)

    def set_installed(value: bool):
        if not installed.done():
            installed.set_result(value)
    loop.call_soon_threadsafe(set_installed, bool(context['hook']))

    if context['hook']:
        # Windows requires a message pump to keep the hook alive
        while user32.GetMessageA(ctypes.byref(msg), 0, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageA(ctypes.byref(msg))


def uninstall_keyboard_hook_proc():
    if context['hook']:
        user32.UnhookWindowsHookEx(context['hook'])
        context['hook'] = None

    # Stop the hook thread message pump
    if context['thread_id']:
        user32.PostThreadMessageW(context['thread_id'], WM_QUIT, 0, 0)
        context['thread_id'] = None


async def install_keyboard_hook_proc():
    loop = asyncio.get_running_loop()
    context['loop'] = loop

    installed = loop.create_future()
    th = threading.Thread(
        target=_install_keyboard_hook_proc,
        args=(installed,),
        daemon=True
    )
    th.start()

    return await installed


def bind(shortcut: str, callback: Callable):
    context['hotkeys'][shortcut].append(callback)


def unbind(shortcut: str, callback: Callable):
    if callback in context['hotkeys'][shortcut]:
        context['hotkeys'][shortcut].remove(callback)


def unbind_all():
    context['hotkeys'].clear()
