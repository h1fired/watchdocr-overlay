from . import CompilerBackend
import subprocess


class NuitkaBackend(CompilerBackend):
    def build(self, module: str, output_dir: str):
        # Add plugins
        s_plugins = []
        for plugin in self.params.plugins:
            s_plugins.append(f'--enable-plugin={plugin}')

        # Add hidden packages
        s_hidden_packages = []
        for pkg in self.params.hidden_packages:
            s_hidden_packages.append(f'--include-package={pkg}')

        # Add custon flags
        s_custom_flags = []
        for flag in self.params.custom_flags:
            s_custom_flags.append(flag)

        cmd = ' '.join([
            'uv run',
            'nuitka',
            '--standalone',
            *s_plugins,
            *s_hidden_packages,
            *s_custom_flags,
            f'--output-dir={output_dir}',
            module
        ])
        subprocess.run(cmd, check=True)

    def dist_folder(self):
        return 'main.dist'
