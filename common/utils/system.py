import ctypes
import psutil


def is_touch_supported():
    touch_input = ctypes.windll.user32.GetSystemMetrics(95)
    return touch_input > 0


def is_battery_exists():
    return psutil.sensors_battery()


def get_battery_percentage() -> int:
    battery = psutil.sensors_battery()
    return battery.percent


def battery_power_plugged() -> bool:
    battery = psutil.sensors_battery()
    return battery.power_plugged
