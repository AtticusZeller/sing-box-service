from typing import Annotated

import typer

from ..common import ensure_root
from .config import SingBoxConfig, get_config

__all__ = ["config", "SingBoxConfig", "get_config"]

config = typer.Typer(help="Configuration management commands")


@config.command("add-sub")
def config_add_sub(ctx: typer.Context, url: Annotated[str, typer.Argument()]) -> None:
    """Add subscription URL"""
    ensure_root()
    if ctx.obj.config.add_subscription(url):
        # restart service if subscription is updated
        if not ctx.obj.service.check_service():
            ctx.obj.service.create_service()
            print("⌛ Service created successfully.")
        if ctx.obj.config.update_config():
            ctx.obj.service.restart()
        else:
            raise typer.Exit(1)
    else:
        print("❌ Failed to add subscription.")
        raise typer.Exit(1)


@config.command("show-sub")
def config_show_sub(ctx: typer.Context) -> None:
    """Show subscription URL"""
    ctx.obj.config.show_subscription()


@config.command("show")
def config_show(ctx: typer.Context) -> None:
    """Show configuration file"""
    ctx.obj.config.show_config()


@config.command("clean_cache")
def config_clean_cache(ctx: typer.Context) -> None:
    """Clean cache database"""
    ctx.obj.config.clean_cache()
