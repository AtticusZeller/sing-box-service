import asyncio
import os
import sys

import typer
from rich import print

from .client import SingBoxAPIClient
from .config import Config
from .connections import ConnectionsManager
from .monitor import ResourceMonitor, ResourceVisualizer
from .policy import PolicyGroupManager
from .run import LinuxRunner, WindowsRunner
from .service import LinuxServiceManager, WindowsServiceManager

app = typer.Typer(help="sing-box service manager.")
service = typer.Typer(help="Service management commands")
config = typer.Typer(help="Configuration management commands")

app.add_typer(service, name="service")
app.add_typer(config, name="config")


class SingBoxCLI:
    def __init__(self) -> None:
        self.config = Config()
        if not self.config.init_directories():
            typer.Exit(1)
        self.service = (
            WindowsServiceManager(self.config)
            if self.config.is_windows
            else LinuxServiceManager(self.config)
        )
        self.runner = (
            WindowsRunner(self.config)
            if self.config.is_windows
            else LinuxRunner(self.config)
        )

    def create_client(
        self, base_url: str | None = None, token: str | None = None
    ) -> SingBoxAPIClient:
        # read from config if not provided
        if base_url is None:
            base_url = self.config.api_base_url
        if token is None:
            token = self.config.api_secret
        return SingBoxAPIClient(base_url, token)

    def ensure_root(self) -> None:
        """https://gist.github.com/RDCH106/fdd419ef7dd803932b16056aab1d2300"""
        try:
            if os.geteuid() != 0:  # type: ignore
                print("⚠️ This script must be run as root.")
                sys.exit(1)
        except AttributeError:
            import ctypes

            if not ctypes.windll.shell32.IsUserAnAdmin():  # type: ignore
                print("⚠️ This script must be run as Administrator.")
                sys.exit(1)


@app.command()
def run() -> None:
    """Run sing-box service"""
    cli = SingBoxCLI()
    cli.ensure_root()
    if cli.config.update_config():
        cli.runner.run()
    else:
        print("❌ Failed to update configuration.")
        typer.Exit(1)


@app.command()
def stats(
    base_url: str | None = typer.Option(
        None,
        "--base-url",
        "-b",
        help="Base URL of the sing-box API, read from configuration file if not provided",
    ),
    token: str | None = typer.Option(
        None,
        "--token",
        "-t",
        help="Authentication token for the sing-box API, read from configuration file if not provided",
    ),
) -> None:
    """Show sing-box traffic, memory statistics and connections, requires API token(Optional)"""
    cli = SingBoxCLI()
    api_client = cli.create_client(base_url, token)
    visualizer = ResourceVisualizer()
    monitor = ResourceMonitor(api_client, visualizer)
    asyncio.run(monitor.start())


@app.command()
def conns(
    base_url: str | None = typer.Option(
        None,
        "--base-url",
        "-b",
        help="Base URL of the sing-box API, read from configuration file if not provided",
    ),
    token: str | None = typer.Option(
        None,
        "--token",
        "-t",
        help="Authentication token for the sing-box API, read from configuration file if not provided",
    ),
) -> None:
    """Manage sing-box connections, requires API token(Optional)"""
    cli = SingBoxCLI()
    api_client = cli.create_client(base_url, token)
    manager = ConnectionsManager(api_client)
    asyncio.run(manager.run())


@app.command()
def proxy(
    base_url: str | None = typer.Option(
        None,
        "--base-url",
        "-b",
        help="Base URL of the sing-box API, read from configuration file if not provided",
    ),
    token: str | None = typer.Option(
        None,
        "--token",
        "-t",
        help="Authentication token for the sing-box API, read from configuration file if not provided",
    ),
) -> None:
    """Manage sing-box policy groups, requires API token(Optional)"""
    cli = SingBoxCLI()
    api_client = cli.create_client(base_url, token)
    manager = PolicyGroupManager(api_client)
    asyncio.run(manager.run())


@service.command("enable")
def service_enable() -> None:
    """Create sing-box service, enable autostart and start service"""
    cli = SingBoxCLI()
    cli.ensure_root()
    cli.service.create_service()
    cli.service.start()
    print("🔥 Service started.")
    print("🔗 Dashboard URL: https://metacubexd.atticux.me/")
    print("🔌 Default API: http://127.0.0.1:9090")


@service.command("disable")
def service_disable() -> None:
    """Stop service, disable sing-box service autostart and remove service"""
    cli = SingBoxCLI()
    cli.ensure_root()
    cli.service.stop()
    cli.service.disable()
    print("✋ Autostart disabled.")


@service.command("restart")
def service_restart() -> None:
    """Restart sing-box service, update configuration if needed, create service if not exists"""
    cli = SingBoxCLI()
    cli.ensure_root()
    if not cli.service.check_service():
        cli.service.create_service()
    if cli.config.update_config():
        cli.service.restart()
    else:
        print("❌ Failed to update configuration.")
        typer.Exit(1)
    print("🔥 Service restarted.")
    print("🔗 Dashboard URL: https://metacubexd.atticux.me/")
    print("🔌 Default API: http://127.0.0.1:9090")


@service.command("stop")
def service_stop() -> None:
    """Stop sing-box service"""
    cli = SingBoxCLI()
    cli.ensure_root()
    cli.service.stop()
    print("✋ Service stopped.")


@service.command("status")
def service_status() -> None:
    """Check service status"""
    cli = SingBoxCLI()
    cli.ensure_root()
    status = cli.service.status()
    print(f"🏃 Service status: {status}")


@service.command("logs")
def service_logs() -> None:
    """Show sing-box service logs"""
    cli = SingBoxCLI()
    cli.service.logs()


@config.command("add-sub")
def config_add_sub(url: str) -> None:
    """Add subscription URL"""
    cli = SingBoxCLI()
    cli.ensure_root()
    if cli.config.add_subscription(url):
        # restart service if subscription is updated
        if not cli.service.check_service():
            cli.service.create_service()
            print("⌛ Service created successfully.")
        if cli.config.update_config():
            cli.service.restart()
        else:
            typer.Exit(1)
    else:
        print("❌ Failed to add subscription.")
        typer.Exit(1)


@config.command("show-sub")
def config_show_sub() -> None:
    """Show subscription URL"""
    cli = SingBoxCLI()
    cli.config.show_subscription()


@config.command("show")
def config_show() -> None:
    """Show configuration file"""
    cli = SingBoxCLI()
    cli.config.show_config()


@config.command("clean_cache")
def config_clean_cache() -> None:
    """Clean cache database"""
    cli = SingBoxCLI()
    cli.config.clean_cache()


@app.command()
def version() -> None:
    """Show version"""
    from . import __version__

    cli = SingBoxCLI()
    print(f"🔖 sing-box-cli {__version__}")
    print(f"📦 {cli.service.version()}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
