import os
import sys

import typer
from rich import print

from .config import Config
from .service import LinuxServiceManager, WindowsServiceManager

app = typer.Typer(help="sing-box service manager.")
service = typer.Typer(help="Service management commands")
config = typer.Typer(help="Configuration management commands")


app.add_typer(service, name="service")
app.add_typer(config, name="config")


class SingBoxCLI:
    def __init__(self) -> None:
        self.config = Config()
        self.service = (
            WindowsServiceManager(self.config)
            if self.config.is_windows
            else LinuxServiceManager(self.config)
        )

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


@service.command("start")
def service_start() -> None:
    """Start sing-box service"""
    cli = SingBoxCLI()
    cli.ensure_root()
    cli.config.init_directories()
    cli.service.create_service()
    cli.service.start()
    print("✅ Service started.")
    print("🔗 Dashboard URL: https://metacubexd.atticux.me/")
    print("🔌 Default API: http://127.0.0.1:9090")


@service.command("stop")
def service_stop() -> None:
    """Stop sing-box service"""
    cli = SingBoxCLI()
    cli.ensure_root()
    cli.service.stop()
    print("✋ Service stopped.")


@service.command("restart")
def service_restart() -> None:
    """Restart sing-box service"""
    cli = SingBoxCLI()
    cli.ensure_root()
    if not cli.service.check_service():
        cli.service.create_service()
        print("⌛ Service created successfully.")
    cli.service.restart()
    print("✅ Service restarted.")
    print("🔗 Dashboard URL: https://metacubexd.atticux.me/")
    print("🔌 Default API: http://127.0.0.1:9090")


@service.command("status")
def service_status() -> None:
    """Check service status"""
    cli = SingBoxCLI()
    cli.ensure_root()
    status = cli.service.status()
    print(f"🏃 Service status: {status}")


@service.command("disable")
def service_disable() -> None:
    """Disable sing-box service autostart"""
    cli = SingBoxCLI()
    cli.ensure_root()
    cli.service.stop()
    cli.service.disable()
    print("✋ Autostart disabled.")


@config.command("add-sub")
def config_add_sub(url: str) -> None:
    """Add subscription URL"""
    cli = SingBoxCLI()
    cli.ensure_root()
    if cli.config.add_subscription(url):
        if cli.config.update_config():
            cli.service.restart()


@config.command("update")
def config_update() -> None:
    """Update configuration from subscription URL"""
    cli = SingBoxCLI()
    cli.ensure_root()
    if cli.config.update_config():
        cli.service.restart()


@config.command("show-sub")
def config_show_sub() -> None:
    """Show subscription URL"""
    cli = SingBoxCLI()
    cli.config.show_subscription()


@config.command("show")
def config_show() -> None:
    """Show configuration"""
    cli = SingBoxCLI()
    cli.config.show_config()


@config.command("clean_cache")
def config_clean_cache() -> None:
    """Clean cache database"""
    cli = SingBoxCLI()
    cli.config.clean_cache()


@app.command()
def logs() -> None:
    """Show sing-box service logs"""
    cli = SingBoxCLI()
    cli.service.logs()


def main() -> None:
    app()


if __name__ == "__main__":
    main()
