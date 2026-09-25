from pathlib import Path
from grpc_tools import protoc
import grpc_tools
from itertools import groupby


PROTOS_DIR = Path('src/backend/transport/grpc/')


def compile_protos():
    grpc_tools_include = Path(grpc_tools.__file__).parent / "_proto"
    protos = sorted(PROTOS_DIR.rglob("*.proto"))

    for dir, files in groupby(protos, lambda p: p.parent):
        files_str = [str(p) for p in files]
        protoc.main([
            "protoc",
            f"-I{dir}",
            f"-I{grpc_tools_include}",
            f"--python_out={dir}",
            f"--pyi_out={dir}",
            f"--grpc_python_out={dir}",
            *list(files_str)
        ])


def run():
    compile_protos()


if __name__ == '__main__':
    run()
