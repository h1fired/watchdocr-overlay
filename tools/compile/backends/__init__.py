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

    def build(self, module: str, output_dir: str, exe_name: str):
        raise NotImplementedError

    def dist_folder(self, module_name: str):
        raise NotImplementedError


@dataclass
class InstallerParams:
    title: str = ''
    version: str = ''
    publisher: str = ''
    icon: str = ''
    exe_name: str = ''
    install_dir_name: str = ''
    app_id: str = ''

    def get_installer_name(self):
        return f'{self.exe_name}_{self.version}_win64'


class InstallerBackend:
    def build(
        self,
        params: InstallerParams,
        output_dir: str,
        exe_dir: str,
        save_dir: str
    ):
        raise NotImplementedError
