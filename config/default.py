import os
from dotenv import load_dotenv


load_dotenv()

DEBUG = True

DEEPL_API_KEY = os.getenv('DEEPL_API_KEY')
QML_WINDOW_FILE = 'frontend/ui/Window.qml'

TRANSLATION_TARGET_LANG = 'UK'

WINDOW_TOGGLE_HOTKEY = 'Alt+B'

MAX_IMAGE_RESOLUTION = (1024, 1024)
