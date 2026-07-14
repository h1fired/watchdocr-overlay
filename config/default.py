from dotenv import load_dotenv
from pathlib import Path
import os
from common.utils.path import create_dir


load_dotenv()


DEBUG = True

APP_ID = 'F450F02A-C03F-4937-B932-B0EE0CD93BE7'
APP_NAME = 'WatchdOcr'
APP_VERSION = '0.1.2_alpha'

USER_SETTINGS_PATH = Path(
    create_dir(os.environ['APPDATA'], APP_NAME),
    'user_settings.yaml'
)

QML_WINDOW_FILE = ':/qml/ui/MainWindow.qml'

PRELOADER_WINDOW_FILE = ':/qml/ui/preloader/AppPreloaderWindow.qml'

PLUGINS_DOWNLOAD_DATA_PATH = Path(
    create_dir(os.environ['LOCALAPPDATA'], APP_NAME),
    'plugdata'
)

OCR_MAX_RECOGNITION_RES = 800
