import asyncio
from functools import lru_cache
from typing import Annotated

import typer

from sing_box_service.config.config import SingBoxConfig

from ..common import StrOrNone
from .client import SingBoxAPIClient
from .connections import ConnectionsManager
from .monitor import ResourceMonitor, ResourceVisualizer
from .policy import PolicyGroupManager

ApiUrlOption = Annotated[
    StrOrNone,
    typer.Option(
        "--base-url",
        "-u",
        help="Base URL of the sing-box API, read from configuration file if not provided",
    ),
]
ApiTokenOption = Annotated[
    StrOrNone,
    typer.Option(
        "--token",
        "-t",
        help="Authentication token for the sing-box API, read from configuration file if not provided",
    ),
]

api = typer.Typer(help="sing-box manager.")


@lru_cache
def create_client(
    config: SingBoxConfig, base_url: StrOrNone = None, token: StrOrNone = None
) -> SingBoxAPIClient:
    # read from config if not provided
    if base_url is None:
        base_url = config.api_base_url
    if token is None:
        token = config.api_secret
    return SingBoxAPIClient(base_url, token)


@api.command()
def stats(
    ctx: typer.Context, base_url: ApiUrlOption = None, token: ApiTokenOption = None
) -> None:
    """Show sing-box traffic, memory statistics and connections, requires API token(Optional)"""

    api_client = create_client(ctx.obj.config, base_url, token)
    visualizer = ResourceVisualizer()
    monitor = ResourceMonitor(api_client, visualizer)
    asyncio.run(monitor.start())


@api.command()
def conns(
    ctx: typer.Context, base_url: ApiUrlOption = None, token: ApiTokenOption = None
) -> None:
    """Manage sing-box connections, requires API token(Optional)"""
    api_client = create_client(ctx.obj.config, base_url, token)
    manager = ConnectionsManager(api_client)
    asyncio.run(manager.run())


@api.command()
def proxy(
    ctx: typer.Context, base_url: ApiUrlOption = None, token: ApiTokenOption = None
) -> None:
    """Manage sing-box policy groups, requires API token(Optional)"""
    api_client = create_client(ctx.obj.config, base_url, token)
    manager = PolicyGroupManager(api_client)
    asyncio.run(manager.run())
