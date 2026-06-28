import os
import argparse
import xml.etree.ElementTree as ET
import subprocess
import sys
from typing import Sequence


class ResourceModel:
    def __init__(
        self,
        dir: str,
        extensions: Sequence[str],
        output: str = '',
        prefix: str = '',
        path_prefix: str = ''
    ):
        self._dir = dir
        self._output = output
        self._prefix = prefix
        self._exts = extensions
        self._path_prefix = path_prefix

    @property
    def directory(self):
        return self._dir

    @property
    def prefix(self):
        return self._prefix

    @property
    def extensions(self):
        return self._exts

    @property
    def path_prefix(self):
        return self._path_prefix

    @property
    def output(self):
        return self._output


class ResourceModelCollection:
    def __init__(self, resources: Sequence[ResourceModel]):
        self._models = resources

    def models(self):
        return self._models


def generate_resources(
    resources: ResourceModelCollection,
    output_file: str = 'resources.qrc',
    prefix: str = '/qml'
):
    RCC = ET.Element('RCC')

    for r in resources.models():
        sub = ET.SubElement(RCC, 'qresource')
        sub.set("prefix", (prefix + '/' + r.prefix) if r.prefix else prefix)

        for dirpath, _, filenames in os.walk(r.directory):
            for filename in filenames:
                if filename.endswith(r.extensions):
                    # Relative path inside resources
                    full_path = os.path.join(dirpath, filename)
                    rel_path = os.path.relpath(full_path, r.directory).replace('\\', '/')
                    file_tag = ET.SubElement(sub, 'file')
                    file_tag.text = os.path.join(r.path_prefix, rel_path)

    # Save XML to file
    tree = ET.ElementTree(RCC)
    ET.indent(tree, space='  ', level=0)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)

    print('Generated resources:')
    for r in resources.models():
        print(f'\t- {os.path.abspath(os.path.join(r.directory, output_file))}')


def compile_resources(*files: Sequence[str], no_init=False):
    for file in files:
        dir = os.path.dirname(file)
        cmd = f'pyside6-rcc -o {dir}/qresources.py {file}'
        try:
            subprocess.run(cmd.split(), cwd=dir)

            if no_init:
                with open(f'{dir}/qresources.py', 'r') as f:
                    lines = f.readlines()
                lines = lines[:-2]
                with open(f'{dir}/qresources.py', 'w') as f:
                    f.writelines(lines)

        except subprocess.CalledProcessError as e:
            raise subprocess.CalledProcessError('Compilation failed') from e

    print('Compiled resources:')
    for file in files:
        print(f'\t- {file} -> qresources.py')


class Styles:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"


def log(text: str, *styles: Styles):
    if sys.stdout.isatty():
        code = ''.join(styles)
        text = f'{code}{text}{Styles.RESET}'
    print(text)


def build_resources(
    generate: bool,
    compile: bool
):
    qml_resource = ResourceModel(
        'frontend/ui',
        ('.qml', '.js'),
        path_prefix='ui/'
    )
    img_resource = ResourceModel(
        'frontend/resources',
        ('.svg', '.png', '.ico', '.ttf'),
        path_prefix='resources'
    )
    resources = ResourceModelCollection([qml_resource, img_resource])

    if generate:
        generate_resources(
            resources,
            output_file='frontend/resources.qrc',
            prefix='/qml'
        )

    if compile:
        compile_resources(
            os.path.abspath('frontend/resources.qrc')
        )

    log('Resources compiled!', Styles.GREEN)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Build resources'
    )
    parser.add_argument(
        '--generate',
        action='store_true',
        help='Generate QRC resources files'
    )
    parser.add_argument(
        '--compile',
        action='store_true',
        help='Compile QRC resources files'
    )
    args = parser.parse_args()

    build_resources(
        args.generate,
        args.compile
    )
