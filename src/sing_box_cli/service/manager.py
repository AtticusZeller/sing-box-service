import shutil
import subprocess
from pathlib import Path

from ..config.config import ConfigHandler, run_cmd


class ServiceManager:
    def __init__(self, config: ConfigHandler) -> None:
        self.config = config

    def create_service(self) -> None:
        raise NotImplementedError()

    def check_service(self) -> bool:
        raise NotImplementedError()

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

    def version(self) -> str:
        raise NotImplementedError()


class WindowsServiceManager(ServiceManager):
    """
    commands: https://nssm.cc/commands
    binary: https://nssm.cc/builds
    """

    def __init__(self, config: ConfigHandler) -> None:
        super().__init__(config)
        self.service_name = "sing-box-service"
        self.status_list = ["SERVICE_RUNNING", "SERVICE_STOPPED", "SERVICE_PAUSED"]

    @property
    def nssm_bin(self) -> str:
        """Get the NSSM executable path"""
        nssm_exe: Path | str | None = shutil.which("nssm")
        if nssm_exe is None:
            bin_dir = Path(__file__).parents[1] / "bin"
            nssm_exe = bin_dir / "nssm.exe"
        return str(nssm_exe)

    def create_service(self) -> None:
        """Create a Windows service using NSSM"""
        # Install the service
        try:
            subprocess.run(
                [
                    self.nssm_bin,
                    "install",
                    self.service_name,
                    *run_cmd(self.config).split(),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            # Service might already exist, which is fine for a create
            pass

        # Automatic startup at boot.
        subprocess.run(
            [self.nssm_bin, "set", self.service_name, "Start", "SERVICE_AUTO_START"],
            check=True,
            stdout=subprocess.DEVNULL,
        )

        # Configure service recovery options
        subprocess.run(
            [self.nssm_bin, "set", self.service_name, "AppExit", "Default", "Restart"],
            check=True,
            stdout=subprocess.DEVNULL,
        )

        subprocess.run(
            [self.nssm_bin, "set", self.service_name, "AppRestartDelay", "2000"],
            check=True,
            stdout=subprocess.DEVNULL,
        )

        # Process priority and CPU affinity
        subprocess.run(
            [
                self.nssm_bin,
                "set",
                self.service_name,
                "AppPriority",
                "HIGH_PRIORITY_CLASS",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )

        # A standalone service. This is the default.
        subprocess.run(
            [
                self.nssm_bin,
                "set",
                self.service_name,
                "Type",
                "SERVICE_WIN32_OWN_PROCESS",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )

    def check_service(self) -> bool:
        """Check if the service exists"""
        result = subprocess.run(
            [self.nssm_bin, "status", self.service_name], capture_output=True, text=True
        )
        return result.stdout.strip() in self.status_list

    def start(self) -> None:
        """Start the service"""
        try:
            subprocess.run(
                [self.nssm_bin, "start", self.service_name],
                check=True,
                stdout=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            pass

    def stop(self) -> None:
        """Stop the service"""
        try:
            subprocess.run(
                [self.nssm_bin, "stop", self.service_name],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            # Service might not be running, which is fine for a stop
            pass

    def restart(self) -> None:
        """Restart the service"""
        subprocess.run(
            [self.nssm_bin, "restart", self.service_name],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def status(self) -> str:
        """Get the service status"""
        result = subprocess.run(
            [self.nssm_bin, "status", self.service_name], capture_output=True, text=True
        )
        return (
            result.stdout.replace("_", " ").title().strip()
            if result.stdout
            else "Service not installed"
        )

    def disable(self) -> None:
        """Remove the service"""
        try:
            subprocess.run(
                [self.nssm_bin, "remove", self.service_name, "confirm"],
                check=True,
                stdout=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            # Service might not exist, which is fine for a disable
            pass

    def version(self) -> str:
        result = subprocess.run([self.config.bin_path, "version"], capture_output=True)
        return result.stdout.decode("utf-8").strip()


class LinuxServiceManager(ServiceManager):
    def __init__(self, config: ConfigHandler) -> None:
        super().__init__(config)
        self.service_name = "sing-box"
        self.service_file = Path("/etc/systemd/system/sing-box.service")

    def create_service(self) -> None:
        """systemctl list-units | grep -i network
        Refs:
            1. https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html#Type
            2. https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#Scheduling
        """
        service_content = f"""
[Unit]
Description=sing-box service
Documentation=https://sing-box.sagernet.org
After=network-online.target nss-lookup.target

[Service]
Type=exec
LimitNOFILE=infinity
CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_RAW CAP_NET_BIND_SERVICE CAP_SYS_TIME CAP_SYS_PTRACE CAP_DAC_READ_SEARCH CAP_DAC_OVERRIDE
AmbientCapabilities=CAP_NET_ADMIN CAP_NET_RAW CAP_NET_BIND_SERVICE CAP_SYS_TIME CAP_SYS_PTRACE CAP_DAC_READ_SEARCH CAP_DAC_OVERRIDE

# restart
Restart=on-failure
RestartSec=5
StartLimitInterval=60
StartLimitBurst=3
# start commands
ExecStart={run_cmd(self.config)}
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
        if self.service_file.exists():
            self.service_file.unlink()

    def version(self) -> str:
        result = subprocess.run([self.config.bin_path, "version"], capture_output=True)
        return result.stdout.decode("utf-8").strip()


def create_service(
    config: ConfigHandler,
) -> WindowsServiceManager | LinuxServiceManager:
    return (
        WindowsServiceManager(config)
        if config.is_windows
        else LinuxServiceManager(config)
    )
