from dotenv import load_dotenv
from pathlib import Path
import os
from common.utils.path import create_dir


load_dotenv()


DEBUG = True

APP_ID = '-'
APP_NAME = 'WatchdOcr'
APP_VERSION = '0.1.0'

USER_SETTINGS_PATH = Path(
    create_dir(os.environ['APPDATA'], APP_NAME),
    'user_settings.yaml'
)

QML_WINDOW_FILE = ':/qml/ui/MainWindow.qml'
WINDOW_TOGGLE_HOTKEY = 'Alt+B'

LIVE_MANAGE_MODE_FREQ = 2
