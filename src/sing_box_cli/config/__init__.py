from typing import Annotated

import typer
from rich import print

from ..common import StrOrNone, ensure_root
from ..service import get_context_obj

__all__ = ["config"]

SubUrlArg = Annotated[str, typer.Argument(help="Subscription URL")]
TokenOption = Annotated[
    StrOrNone,
    typer.Option("--token", "-t", help="Authentication token for the subscription URL"),
]
RestartServiceOption = Annotated[
    bool, typer.Option("--restart", "-r", help="Restart service after update.")
]
config = typer.Typer(help="Configuration management commands")


@config.command("update")
def config_update(
    ctx: typer.Context,
    url: SubUrlArg,
    token: TokenOption = None,
    restart: RestartServiceOption = False,
) -> None:
    """download configuration, save subscription url and restart service if needed"""
    ctx_obj = get_context_obj(ctx)
    if ctx_obj.config.update_config(url, token):
        pass
    else:
        print("❌ Failed to update configuration.")
        raise typer.Exit(1)
    if restart:
        ensure_root()
        # init service
        if not ctx_obj.service.check_service():
            ctx_obj.service.create_service()
            print("⌛ Service created successfully.")
        ctx_obj.service.restart()


@config.command("show-sub")
def config_show_sub(ctx: typer.Context) -> None:
    """Show subscription URL"""
    ctx_obj = get_context_obj(ctx)
    sub_url = ctx_obj.config.sub_url
    if sub_url:
        print(f"🔗 Current subscription URL: {sub_url}")
    else:
        print("❌ No subscription URL found.")


@config.command("show")
def config_show(ctx: typer.Context) -> None:
    """Show configuration file"""
    ctx_obj = get_context_obj(ctx)
    print(ctx_obj.config.config_file_content)


@config.command("clear_cache")
def config_clear_cache(ctx: typer.Context) -> None:
    """Clean cache database"""
    ctx_obj = get_context_obj(ctx)
    ctx_obj.config.clear_cache()
