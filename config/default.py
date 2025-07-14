import os
from dotenv import load_dotenv


load_dotenv()

DEBUG = True
DEEPL_API_KEY = os.getenv('DEEPL_API_KEY')
QML_WINDOW_FILE = 'frontend/ui/window.qml'

TRANSLATION_TARGET_LANG = 'UK'
