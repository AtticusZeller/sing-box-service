import shutil
import subprocess
from pathlib import Path

from ..config.config import SingBoxConfig


class ServiceManager:
    def __init__(self, config: SingBoxConfig) -> None:
        self.config = config

    @property
    def run_cmd(self) -> str:
        """Get the run command for the service"""
        return f"{self.config.bin_path} run -C {self.config.config_dir} -D {self.config.config_dir}"

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
    def __init__(self, config: SingBoxConfig) -> None:
        super().__init__(config)
        self.task_name = "sing-box-service"

    @property
    def pwsh(self) -> Path:
        """Get the PowerShell executable path"""
        # Use the pwsh executable if available, otherwise fall back to windows powershell
        pwsh_exe = shutil.which("pwsh") or shutil.which("powershell")

        if pwsh_exe:
            return Path(pwsh_exe).resolve()
        else:
            raise OSError("PowerShell is not installed.")

    def create_service(self) -> None:
        ps_command = f"""
$action = New-ScheduledTaskAction `
    -Execute "{self.pwsh}" `
    -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -Command `"{self.run_cmd}`""

$trigger = New-ScheduledTaskTrigger -AtLogOn
$principal = New-ScheduledTaskPrincipal -UserId "{self.config.user}" -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable -Priority 0 -DontStopIfGoingOnBatteries -DontStopOnIdleEnd -RestartCount 10

Register-ScheduledTask -TaskName "{self.task_name}" `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Settings $settings `
    -Force
"""
        subprocess.run([self.pwsh, "-Command", ps_command], check=True)

    def check_service(self) -> bool:
        ps_command = f"Get-ScheduledTask -TaskName '{self.task_name}' -ErrorAction SilentlyContinue"
        result = subprocess.run(
            [self.pwsh, "-Command", ps_command], capture_output=True
        )
        return result.returncode == 0

    def start(self) -> None:
        subprocess.run(
            [self.pwsh, "-Command", f"Start-ScheduledTask -TaskName '{self.task_name}'"]
        )

    def stop(self) -> None:
        subprocess.run(
            [self.pwsh, "-Command", f"Stop-ScheduledTask -TaskName '{self.task_name}'"]
        )

    def restart(self) -> None:
        self.stop()
        self.start()

    def status(self) -> str:
        ps_command = f"""
$task = Get-ScheduledTask -TaskName '{self.task_name}' -ErrorAction SilentlyContinue
if ($task) {{
    $process = Get-Process | Where-Object {{ $_.Path -eq '{self.config.bin_path}' }}
    if ($process) {{
        "Running (PID: $($process.Id))"
    }} else {{
        "Stopped"
    }}
}} else {{
    "Not installed"
}}
"""
        result = subprocess.run(
            [self.pwsh, "-Command", ps_command], capture_output=True, text=True
        )
        return result.stdout.strip()

    def disable(self) -> None:
        self.stop()
        subprocess.run(
            [
                self.pwsh,
                "-Command",
                f"Unregister-ScheduledTask -TaskName '{self.task_name}' -Confirm:$false",
            ]
        )

    def version(self) -> str:
        result = subprocess.run([self.config.bin_path, "version"], capture_output=True)
        return result.stdout.decode("utf-8").strip()


class LinuxServiceManager(ServiceManager):
    def __init__(self, config: SingBoxConfig) -> None:
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
Restart=always
RestartSec=2
# start commands
ExecStart={self.run_cmd}
ExecReload=/bin/kill -HUP $MAINPID
# IO
IOSchedulingPriority=0
IOSchedulingClass=realtime
# CPU
CPUSchedulingPolicy=rr
CPUSchedulingPriority=99
Nice=-20

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
    config: SingBoxConfig,
) -> WindowsServiceManager | LinuxServiceManager:
    return (
        WindowsServiceManager(config)
        if config.is_windows
        else LinuxServiceManager(config)
    )
