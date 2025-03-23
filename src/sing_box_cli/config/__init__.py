from typing import Annotated

import typer

from ..common import StrOrNone, ensure_root
from .config import SingBoxConfig, get_config

__all__ = ["config", "SingBoxConfig", "get_config"]

SubUrlArg = Annotated[str, typer.Argument(help="Subscription URL")]
TokenOption = Annotated[
    StrOrNone,
    typer.Option("--token", "-t", help="Authentication token for the subscription URL"),
]
RestartServiceOption = Annotated[
    bool, typer.Option("--restart", "-r", help="Restart service after update.")
]
config = typer.Typer(help="Configuration management commands")


# TODO: save url for update if provided
@config.command("update")
def config_update(
    ctx: typer.Context,
    url: SubUrlArg,
    token: TokenOption = None,
    restart: RestartServiceOption = False,
) -> None:
    """download configuration, save subscription url and restart service if needed"""
    if ctx.obj.config.update_config(url, token):
        pass
    else:
        print("❌ Failed to update configuration.")
        raise typer.Exit(1)
    if restart:
        ensure_root()
        # init service
        if not ctx.obj.service.check_service():
            ctx.obj.service.create_service()
            print("⌛ Service created successfully.")
        ctx.obj.service.restart()


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
