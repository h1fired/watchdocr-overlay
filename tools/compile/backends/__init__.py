from dataclasses import dataclass, field


@dataclass(slots=True)
class CompilerParams:
    plugins: list = field(default_factory=list)
    hidden_packages: list = field(default_factory=list)
    custom_flags: list = field(default_factory=list)


class CompilerBackend:
    def __init__(self):
        self._params = CompilerParams()

    @property
    def params(self):
        return self._params

    def build(self, module: str, output_dir: str):
        raise NotImplementedError

    def dist_folder(self):
        raise NotImplementedError
