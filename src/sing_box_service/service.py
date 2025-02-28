import subprocess
from pathlib import Path

from .config import Config


class ServiceManager:
    def __init__(self, config: Config):
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

    def logs(self) -> None:
        raise NotImplementedError()

    def disable(self) -> None:
        raise NotImplementedError()


class WindowsServiceManager(ServiceManager):
    def __init__(self, config: Config):
        super().__init__(config)
        self.task_name = "sing-box-service"
        self.log_file = self.config.install_dir / "sing-box.log"

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

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

Set-Location "{self.config.install_dir}"

if (Test-Path "{self.log_file}") {{
    Clear-Content "{self.log_file}"
}}

try {{
    & "{self.config.bin_path}" run -C "{self.config.install_dir}" *>&1 | Tee-Object -FilePath "{self.log_file}" -Append
}} catch {{
    $_ | Out-File -FilePath "{self.log_file}" -Append
}}
"""
        start_script.write_text(script_content, encoding="utf-8")

        ps_command = f"""
$action = New-ScheduledTaskAction `
    -Execute "pwsh.exe" `
    -Argument "-ExecutionPolicy Bypass -NoLogo -WindowStyle Hidden -File `"{start_script}`""

$trigger = New-ScheduledTaskTrigger -AtLogon
$principal = New-ScheduledTaskPrincipal -UserId "{self.config.user}" -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

Register-ScheduledTask -TaskName "{self.task_name}" `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Settings $settings `
    -Force
"""
        subprocess.run(["pwsh", "-Command", ps_command], check=True)

    def check_service(self) -> bool:
        ps_command = f"Get-ScheduledTask -TaskName '{self.task_name}' -ErrorAction SilentlyContinue"
        result = subprocess.run(["pwsh", "-Command", ps_command], capture_output=True)
        return result.returncode == 0

    def start(self) -> None:
        subprocess.run(
            ["pwsh", "-Command", f"Start-ScheduledTask -TaskName '{self.task_name}'"]
        )

    def stop(self) -> None:
        subprocess.run(
            ["pwsh", "-Command", f"Stop-ScheduledTask -TaskName '{self.task_name}'"]
        )
        ps_command = "Get-Process | Where-Object { $_.ProcessName -eq 'sing-box' } | Stop-Process -Force"
        subprocess.run(["pwsh", "-Command", ps_command])

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
            ["pwsh", "-Command", ps_command], capture_output=True, text=True
        )
        return result.stdout.strip()

    def logs(self) -> None:
        if not self.log_file.exists():
            print("⚠️ Log file not found")
            return
        try:
            print("⌛ Showing real-time logs (Press Ctrl+C to exit)")
            ps_command = (
                f"Get-Content -Path '{self.log_file}' -Wait -Tail 50 -Encoding UTF8"
            )
            subprocess.run(["pwsh", "-Command", ps_command])
        except KeyboardInterrupt:
            return

    def disable(self) -> None:
        self.stop()
        subprocess.run(
            [
                "pwsh",
                "-Command",
                f"Unregister-ScheduledTask -TaskName '{self.task_name}' -Confirm:$false",
            ]
        )


class LinuxServiceManager(ServiceManager):
    def __init__(self, config: Config):
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
ExecStart={self.config.bin_path} run -C {self.config.install_dir} -D {self.config.install_dir}
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

    def logs(self) -> None:
        print("⌛ Showing real-time logs (Press Ctrl+C to exit)")
        subprocess.run(["journalctl", "-u", "sing-box", "-o", "cat", "-f"])

    def disable(self) -> None:
        self.stop()
        subprocess.run(["systemctl", "disable", self.service_name])
