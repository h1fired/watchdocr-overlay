import os


def get_user_dir(path: str):
    return os.path.expanduser(f'~\\{path}')


def create_dir(path: str, name: str):
    if not os.path.exists(f'{path}\\{name}'):
        os.makedirs(f'{path}\\{name}')

    return f'{path}\\{name}'


def get_appdata_path():
    return os.getenv('APPDATA', None)


def find_files(root: str, filename: str):
    files = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn == filename:
                files.append(os.path.abspath(os.path.join(dirpath, fn)))
    return files
