from dotenv import load_dotenv
from pathlib import Path
import os
from common.utils.path import create_dir


load_dotenv()


DEBUG = True

APP_NAME = 'WatchdOcr'

USER_SETTINGS_PATH = Path(
    create_dir(os.environ['APPDATA'], APP_NAME),
    'user_settings.yaml'
)

QML_WINDOW_FILE = 'frontend/ui/MainWindow.qml'
WINDOW_TOGGLE_HOTKEY = 'Alt+B'
