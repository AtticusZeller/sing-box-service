import subprocess

from sing_box_service.config import Config


class RunnerBase:
    def __init__(self, config: Config) -> None:
        self.config = config

    def run(self) -> None:
        self._cmd(str(self.config.install_dir), str(self.config.install_dir))

    def _cmd(self, cfg_dir: str, cwd: str) -> None:
        raise NotImplementedError


class WindowsRunner(RunnerBase):
    def _cmd(self, cfg_dir: str, cwd: str) -> None:
        subprocess.run(["pwsh", self.config.bin_path, "run", "-C", cfg_dir, "-D", cwd])


class LinuxRunner(RunnerBase):
    def _cmd(self, cfg_dir: str, cwd: str) -> None:
        subprocess.run([self.config.bin_path, "run", "-C", cfg_dir, "-D", cwd])
