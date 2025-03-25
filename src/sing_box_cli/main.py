import subprocess
from dataclasses import dataclass

import typer
from rich import print

from .api import api as api_app
from .common import UpdateConfigOption, ensure_root
from .config import SingBoxConfig, config as config_app, get_config
from .service import (
    LinuxServiceManager,
    WindowsServiceManager,
    create_service,
    service as service_app,
)


@dataclass
class SharedContext:
    config: SingBoxConfig
    service: WindowsServiceManager | LinuxServiceManager


app = typer.Typer(help="sing-box manager.")
app.add_typer(api_app)
app.add_typer(service_app, name="service")
app.add_typer(config_app, name="config")


@app.callback(invoke_without_command=False)
def callback(ctx: typer.Context) -> None:
    cfg = get_config()
    service = create_service(cfg)
    ctx.obj = SharedContext(config=cfg, service=service)


@app.command()
def run(ctx: typer.Context, update: UpdateConfigOption = False) -> None:
    """Run sing-box if host's service unavailable"""
    ensure_root()
    cfg = ctx.obj.config
    if update:
        if cfg.update_config():
            print("✅ Configuration updated.")
        else:
            print("❌ Failed to update configuration.")
            raise typer.Exit(1)

    cmd = [cfg.bin_path, "run", "-C", str(cfg.config_dir), "-D", str(cfg.config_dir)]
    subprocess.run(cmd)


@app.command()
def version(ctx: typer.Context) -> None:
    """Show version"""
    from . import __version__

    print(f"🔖 sing-box-cli {__version__}")
    print(f"📦 {ctx.obj.service.version()}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
