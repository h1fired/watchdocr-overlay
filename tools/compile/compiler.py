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
from pathlib import Path
import shutil
import argparse
import subprocess


COMPILE_DIR_NAME = 'compile'
OUTPUT_DIR_NAME = 'output'


class CompilerBackends(Enum):
    NUITKA = NuitkaBackend


class InstallerBackends(Enum):
    INNO = InnoBackend


class BuildOption(IntFlag):
    BUILD_INSTALLER = 1
    BUILD_PORTABLE = 2


class PluginPackageFinder:
    def __init__(self, base_package: str, exclude: list[str] = None):
        self.base_package = base_package
        self.exclude = set(exclude) if exclude else set()

    def find_packages(self) -> list[str]:
        base_path = Path(self.base_package.replace('.', '/'))
        if not base_path.is_dir():
            return [self.base_package]

        packages = [self.base_package]
        for sub_dir in base_path.iterdir():
            if not sub_dir.is_dir() or sub_dir.name == '__pycache__':
                continue
            category_package = f'{self.base_package}.{sub_dir.name}'
            packages.append(category_package)
            for child in sub_dir.iterdir():
                if child.is_dir() and child.name != '__pycache__':
                    if child.name not in self.exclude:
                        packages.append(f'{category_package}.{child.name}')
        return packages

    def find_data_dirs(self) -> list[str]:
        base_path = Path(self.base_package.replace('.', '/'))
        if not base_path.is_dir():
            return []

        data_dirs = []
        for sub_dir in base_path.iterdir():
            if not sub_dir.is_dir() or sub_dir.name == '__pycache__':
                continue
            for child in sub_dir.iterdir():
                if child.is_dir() and child.name != '__pycache__':
                    if child.name not in self.exclude:
                        data_folder = child / 'data'
                        if data_folder.is_dir():
                            data_dirs.append(data_folder.as_posix())
        return data_dirs

    def find_data_files(self, extensions: list[str] = None) -> list[str]:
        if extensions is None:
            extensions = ['.dll', '.pyd', '.so']
        extensions = {ext.lower() for ext in extensions}

        files = []
        for data_dir in self.find_data_dirs():
            data_path = Path(data_dir)
            for file_path in data_path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in extensions:
                    files.append(file_path.as_posix())
        return files


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
        self.icon = os.path.normpath(self.icon)
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

        self._removable_files: list[str] = []

    @property
    def compiler_params(self):
        return self._compiler.params

    def add_removable_file(self, file: str):
        self._removable_files.append(file)

    def build(self, module: str, options: BuildOption):
        # Build resources
        cmd = ' '.join([
            'uv run tools/resources.py',
            '--generate',
            '--compile',
        ])
        subprocess.run(cmd, check=True)

        # Build app
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

        shutil.move(
            f'{compile_dir}/build/{self._compiler.dist_folder(Path(module).stem)}',
            f'{compile_dir}/dist'
        )

        for file in self._removable_files:
            full_path = os.path.join(compile_dir, 'dist', file)
            os.remove(full_path)

        if options & BuildOption.BUILD_INSTALLER:
            params = InstallerParams(
                title=self._config.title,
                version=self._config.version,
                publisher=self._config.publisher,
                icon=os.path.normpath(f'{compile_dir}/logo.ico'),
                exe_name=self._config.exe_name,
                install_dir_name=self._config.install_dir_name,
                app_id=self._config.app_id
            )
            self._installer.build(
                params=params,
                output_dir=OUTPUT_DIR_NAME,
                exe_dir='dist',
                save_dir=compile_dir
            )
        if options & BuildOption.BUILD_PORTABLE:
            # Create portable version
            print('Create portable version...')
            shutil.make_archive(
                f'{compile_dir}/{OUTPUT_DIR_NAME}/{self._config.portable_fn}',
                'zip',
                f'{compile_dir}/dist'
            )

        # Clean up
        logo_path = f'{compile_dir}/logo.ico'
        if os.path.exists(logo_path):
            os.remove(logo_path)

        shutil.rmtree(f'{compile_dir}/build')

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

    # Exclude plugins if needed by listing their folder names in the exclude parameter
    finder = PluginPackageFinder('src.watchdocr.plugins')
    builder.compiler_params.hidden_packages.extend(finder.find_packages())

    for data_dir in finder.find_data_dirs():
        builder.compiler_params.custom_flags.append(f'--include-data-dir={data_dir}={data_dir}')

    for data_file in finder.find_data_files():
        builder.compiler_params.custom_flags.append(f'--include-data-files={data_file}={data_file}')

    builder.compiler_params.hidden_packages.append('winrt')
    builder.compiler_params.custom_flags.append('--include-qt-plugins=qml')
    builder.compiler_params.custom_flags.append('--include-windows-runtime-dlls=yes')
    builder.compiler_params.custom_flags.append('--windows-disable-console')

    builder.add_removable_file('qt6webenginecore.dll')

    options = 0
    if args.installer:
        options |= BuildOption.BUILD_INSTALLER
    if args.portable:
        options |= BuildOption.BUILD_PORTABLE

    builder.build('main.py', options)
