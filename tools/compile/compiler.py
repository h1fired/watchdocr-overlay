import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from common.utils.exception import DebugError
from tools.compile.backends import CompilerBackend, InstallerBackend
from tools.compile.backends.nuitka import NuitkaBackend
from tools.compile.backends.inno import InnoBackend, InstallerParams
from dataclasses import dataclass
from config import default
from enum import Enum, IntFlag
from datetime import datetime
from PIL import Image
import shutil
import argparse


COMPILE_DIR_NAME = 'compile'
OUTPUT_DIR_NAME = 'output'


class CompilerBackends(Enum):
    NUITKA = NuitkaBackend


class InstallerBackends(Enum):
    INNO = InnoBackend


class BuildOption(IntFlag):
    BUILD_INSTALLER = 1
    BUILD_PORTABLE = 2


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
    def __init__(
        self,
        config: AppConfig,
        compiler_backend: CompilerBackends,
        installer_backend: InstallerBackends
    ):
        self._config = config
        self._compiler: CompilerBackend = compiler_backend.value()
        self._installer: InstallerBackend = installer_backend.value()

    @property
    def compiler_params(self):
        return self._compiler.params

    def build(self, module: str, options: BuildOption):
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
        self._compiler.build(
            module,
            os.path.join(compile_dir, 'build'),
            self._config.exe_name
        )

        # Clean up
        shutil.move(
            f'{compile_dir}/build/{self._compiler.dist_folder()}',
            f'{compile_dir}/dist'
        )
        os.remove(f'{compile_dir}/logo.ico')
        shutil.rmtree(f'{compile_dir}/build')

        if options & BuildOption.BUILD_INSTALLER:
            params = InstallerParams(
                title=self._config.title,
                version=self._config.version,
                publisher=self._config.publisher,
                icon=self._config.icon,
                exe_name=self._config.exe_name,
                install_dir_name=self._config.install_dir_name,
                app_id=self._config.app_id
            )
            self._installer.build(
                params=params,
                output_dir=OUTPUT_DIR_NAME,
                exe_dir='dist/',
                save_dir=compile_dir
            )

        print('Compiling completed!')


if __name__ == '__main__':
    if default.DEBUG:
        raise DebugError(
            'Unable to compile application '
            'in debug mode (DEBUG=True)'
        )

    parser = argparse.ArgumentParser(prog='App builder')
    parser.add_argument('--installer', action='store_true', help='build installer')
    parser.add_argument('--portable', action='store_true', help='build portable version')
    args = parser.parse_args()

    config = AppConfig(
        title='WatchdOcr',
        version=default.APP_VERSION,
        publisher='H1FIRED',
        icon='frontend/resources/icons/app/app.ico',
        exe_name='watchdocr',
        install_dir_name='WatchdOcr'
    )

    builder = AppBuilder(
        config=config,
        compiler_backend=CompilerBackends.NUITKA,
        installer_backend=InstallerBackends.INNO
    )

    builder.compiler_params.plugins.append('pyside6')
    builder.compiler_params.custom_flags.append('--include-qt-plugins=qml')
    builder.compiler_params.custom_flags.append('--include-windows-runtime-dlls=yes')
    builder.compiler_params.hidden_packages.append('src.watchdocr.plugins')
    builder.compiler_params.hidden_packages.append('winrt')

    options = 0
    if args.installer:
        options |= BuildOption.BUILD_INSTALLER
    if args.portable:
        options |= BuildOption.BUILD_PORTABLE

    builder.build('main.py', options)
