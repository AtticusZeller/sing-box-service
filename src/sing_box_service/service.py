import subprocess
from pathlib import Path

import psutil
from rich import print

from .config import Config


class ServiceManager:
    def __init__(self, config: Config):
        self.config = config

    def create_service(self) -> None:
        raise NotImplementedError()

    def check_service(self) -> bool:
        raise NotImplementedError()

    def init_service(self) -> None:
        if not self.check_service():
            print("⌛ Creating service...")
            self.create_service()

    def start(self) -> None:
        raise NotImplementedError()

    def stop(self) -> None:
        raise NotImplementedError()

    def restart(self) -> None:
        raise NotImplementedError()

    def status(self) -> str:
        raise NotImplementedError()

    def disable(self) -> None:
        raise NotImplementedError()


class WindowsServiceManager(ServiceManager):
    def __init__(self, config: Config):
        super().__init__(config)
        self.task_name = "sing-box"

    def create_service(self) -> None:
        start_script = self.config.install_dir / "start-singbox.ps1"
        script_content = f"""
        Add-Type -Name Window -Namespace Console -MemberDefinition '
        [DllImport("Kernel32.dll")]
        public static extern IntPtr GetConsoleWindow();
        [DllImport("user32.dll")]
        public static extern bool ShowWindow(IntPtr hWnd, Int32 nCmdShow);
        '
        $console = [Console.Window]::GetConsoleWindow()
        [Console.Window]::ShowWindow($console, 0)

        Set-Location "{self.config.install_dir}"
        & "{self.config.bin_path}" tools synctime -w -C "{self.config.install_dir}"
        & "{self.config.bin_path}" run -C "{self.config.install_dir}"
        """
        start_script.write_text(script_content)

        subprocess.run(
            [
                "schtasks",
                "/create",
                "/tn",
                self.task_name,
                "/tr",
                f"powershell -ExecutionPolicy Bypass -File {start_script}",
                "/sc",
                "onlogon",
                "/ru",
                self.config.user,
                "/rl",
                "HIGHEST",
                "/f",
            ]
        )

    def check_service(self) -> bool:
        try:
            subprocess.run(
                ["schtasks", "/query", "/tn", self.task_name],
                capture_output=True,
                check=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def start(self) -> None:
        subprocess.run(["schtasks", "/run", "/tn", self.task_name])

    def stop(self) -> None:
        subprocess.run(["schtasks", "/end", "/tn", self.task_name])
        for proc in psutil.process_iter(["name"]):
            if proc.info["name"] == "sing-box.exe":
                proc.kill()

    def restart(self) -> None:
        self.stop()
        self.start()

    def status(self) -> str:
        try:
            output = subprocess.check_output(
                ["schtasks", "/query", "/tn", self.task_name]
            )
            return "Running" if "Running" in output.decode() else "Stopped"
        except Exception:
            return "Not installed"

    def disable(self) -> None:
        self.stop()
        subprocess.run(["schtasks", "/delete", "/tn", self.task_name, "/f"])


class LinuxServiceManager(ServiceManager):
    def __init__(self, config: Config):
        super().__init__(config)
        self.service_name = "sing-box"
        self.service_file = Path("/etc/systemd/system/sing-box.service")

    def create_service(self) -> None:
        service_content = f"""
[Unit]
Description=sing-box service
Documentation=https://sing-box.sagernet.org
After=network.target nss-lookup.target

[Service]
Type=simple
LimitNPROC=500
LimitNOFILE=1000000
CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_RAW CAP_NET_BIND_SERVICE CAP_SYS_TIME CAP_SYS_PTRACE CAP_DAC_READ_SEARCH CAP_DAC_OVERRIDE
AmbientCapabilities=CAP_NET_ADMIN CAP_NET_RAW CAP_NET_BIND_SERVICE CAP_SYS_TIME CAP_SYS_PTRACE CAP_DAC_READ_SEARCH CAP_DAC_OVERRIDE
Restart=always
ExecStartPre={self.config.bin_path} tools synctime -w -C {self.config.install_dir}
ExecStart={self.config.bin_path} run -C {self.config.install_dir}
ExecReload=/bin/kill -HUP $MAINPID

[Install]
WantedBy=multi-user.target
"""
        self.service_file.write_text(service_content)
        subprocess.run(["systemctl", "daemon-reload"])
        subprocess.run(["systemctl", "enable", self.service_name])

    def check_service(self) -> bool:
        return self.service_file.exists()

    def start(self) -> None:
        subprocess.run(["systemctl", "start", self.service_name])

    def stop(self) -> None:
        subprocess.run(["systemctl", "stop", self.service_name])

    def restart(self) -> None:
        subprocess.run(["systemctl", "restart", self.service_name])

    def status(self) -> str:
        try:
            subprocess.check_call(["systemctl", "is-active", self.service_name])
            return "Running"
        except Exception:
            return "Stopped"

    def disable(self) -> None:
        self.stop()
        subprocess.run(["systemctl", "disable", self.service_name])
