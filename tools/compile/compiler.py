import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from common.utils.exception import DebugError
from tools.compile.backends import CompilerBackend
from tools.compile.backends.nuitka import NuitkaBackend
from dataclasses import dataclass
from config import default
from enum import Enum
from datetime import datetime
from PIL import Image
import shutil


COMPILE_DIR_NAME = 'compile'
OUTPUT_DIR_NAME = 'output'


class CompilerBackends(Enum):
    NUITKA = NuitkaBackend


@dataclass
class AppConfig:
    title: str
    version: str
    publisher: str
    icon: str
    exe_name: str
    install_dir_name: str
    app_id: str = default.APP_ID

    def __post_init__(self):
        self.installer_fn = f'{self.exe_name}_{self.version}_win64'
        self.portable_fn = f'{self.exe_name}_{self.version}_win64-portable'


class AppBuilder:
    def __init__(self, config: AppConfig, compiler_backend: CompilerBackends):
        self._config = config
        self._compiler: CompilerBackend = compiler_backend.value()

    @property
    def compiler_params(self):
        return self._compiler.params

    def build(self, module: str):
        datestamp = datetime.strftime(datetime.now(), "%d-%m-%Y-%H-%M-%S")
        compile_dir = f'{COMPILE_DIR_NAME}_{datestamp}'

        # Create compile folder
        print(f'Creating compile folder "{compile_dir}"')
        os.makedirs(compile_dir)

        # Create icon
        print('Creating app icon...')
        img = Image.open(self._config.icon)
        if img.size != (256, 256):
            raise ValueError('Icon size must be 256x256')
        img.save(f'{compile_dir}/logo.ico')
        self._config.icon = 'logo.ico'

        print('Build executable from .py module...')
        self._compiler.build(module, os.path.join(compile_dir, 'build'))

        # Clean up
        shutil.move(
            f'{compile_dir}/build/{self._compiler.dist_folder()}',
            f'{compile_dir}/dist'
        )
        os.remove(f'{compile_dir}/logo.ico')
        shutil.rmtree(f'{compile_dir}/build')

        print('Compiling completed!')


if __name__ == '__main__':
    if default.DEBUG:
        raise DebugError(
            'Unable to compile application '
            'in debug mode (DEBUG=True)'
        )

    # parser = argparse.ArgumentParser(prog='App builder')
    # parser.add_argument('--installer', action='store_true', help='build installer')
    # parser.add_argument('--portable', action='store_true', help='build portable version')
    # args = parser.parse_args()

    config = AppConfig(
        title='WatchdOcr',
        version=default.APP_VERSION,
        publisher='H1FIRED',
        icon='frontend/resources/icons/app/256x256.png',
        exe_name='watchocr',
        install_dir_name='WatchdOcr'
    )

    builder = AppBuilder(
        config=config,
        compiler_backend=CompilerBackends.NUITKA
    )

    builder.compiler_params.plugins.append('pyside6')
    builder.compiler_params.custom_flags.append('--include-qt-plugins=qml')
    builder.compiler_params.custom_flags.append('--include-windows-runtime-dlls=yes')
    builder.compiler_params.hidden_packages.append('src.watchdocr.plugins')
    builder.compiler_params.hidden_packages.append('winrt')

    builder.build('main.py')
