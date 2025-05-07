import asyncio
from typing import Annotated

import typer

from ..common import LogLevel, StrOrNone
from ..config.config import ConfigHandler
from ..service import get_context_obj
from .client import SingBoxAPIClient
from .connections import ConnectionsManager
from .logs import get_logs
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

LogLevelOption = Annotated[
    LogLevel,
    typer.Option(
        "--log-level",
        "-l",
        help="Log level of trace, debug, info, warning, error, fatal, panic",
        case_sensitive=False,
    ),
]

api = typer.Typer(help="sing-box manager.")


def create_client(
    config: ConfigHandler, base_url: StrOrNone = None, token: StrOrNone = None
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
    ctx_obj = get_context_obj(ctx)
    api_client = create_client(ctx_obj.config, base_url, token)
    visualizer = ResourceVisualizer()
    monitor = ResourceMonitor(api_client, visualizer)
    asyncio.run(monitor.start())


@api.command()
def conns(
    ctx: typer.Context, base_url: ApiUrlOption = None, token: ApiTokenOption = None
) -> None:
    """Manage sing-box connections, requires API token(Optional)"""
    ctx_obj = get_context_obj(ctx)
    api_client = create_client(ctx_obj.config, base_url, token)
    manager = ConnectionsManager(api_client)
    asyncio.run(manager.run())


@api.command()
def proxy(
    ctx: typer.Context, base_url: ApiUrlOption = None, token: ApiTokenOption = None
) -> None:
    """Manage sing-box policy groups, requires API token(Optional)"""
    ctx_obj = get_context_obj(ctx)
    api_client = create_client(ctx_obj.config, base_url, token)
    manager = PolicyGroupManager(api_client)
    asyncio.run(manager.run())


@api.command()
def logs(
    ctx: typer.Context,
    log_level: LogLevelOption = LogLevel.info,
    base_url: ApiUrlOption = None,
    token: ApiTokenOption = None,
) -> None:
    """Show sing-box logs, requires API token(Optional)"""
    ctx_obj = get_context_obj(ctx)
    api_client = create_client(ctx_obj.config, base_url, token)
    print("⌛ Showing real-time logs (Press Ctrl+C to exit)")
    asyncio.run(get_logs(api_client, log_level))
