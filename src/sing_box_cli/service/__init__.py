from dataclasses import dataclass
from typing import cast

import typer

from ..common import ClearCacheOption, UpdateConfigOption, ensure_root
from ..config.config import ConfigHandler
from .manager import LinuxServiceManager, WindowsServiceManager

__all__ = ["service", "SharedContext", "get_context_obj"]


service = typer.Typer(help="Service management commands")


@dataclass
class SharedContext:
    config: ConfigHandler
    service: WindowsServiceManager | LinuxServiceManager


def get_context_obj(ctx: typer.Context) -> SharedContext:
    return cast(SharedContext, ctx.obj)


@service.command("enable")
def service_enable(ctx: typer.Context) -> None:
    """Create sing-box service, enable autostart and start service"""
    ensure_root()
    ctx_obj = get_context_obj(ctx)
    config = ctx_obj.config
    service = ctx_obj.service
    service.create_service()
    service.start()
    print("🔥 Service started.")
    if config.api_base_url:
        print(f"🔌 Default API: {config.api_base_url}")


@service.command("disable")
def service_disable(ctx: typer.Context) -> None:
    """Stop service, disable sing-box service autostart and remove service"""
    ensure_root()
    ctx_obj = get_context_obj(ctx)
    service = ctx_obj.service
    service.stop()
    service.disable()
    print("✋ Autostart disabled.")


@service.command("restart")
def service_restart(
    ctx: typer.Context,
    update: UpdateConfigOption = False,
    purge: ClearCacheOption = False,
) -> None:
    """Restart sing-box service, update configuration if needed, create service if not exists"""
    ensure_root()
    ctx_obj = get_context_obj(ctx)
    config = ctx_obj.config
    service = ctx_obj.service
    if not service.check_service():
        service.create_service()
    if update:
        if config.update_config():
            pass
        else:
            print("❌ Failed to update configuration.")
            raise typer.Exit(1)
    service.stop()
    if purge:
        config.clear_cache()
    service.start()
    print("🔥 Service restarted.")
    if config.api_base_url:
        print(f"🔌 Default API: {config.api_base_url}")


@service.command("stop")
def service_stop(ctx: typer.Context) -> None:
    """Stop sing-box service"""
    ensure_root()
    ctx_obj = get_context_obj(ctx)
    service = ctx_obj.service
    service.stop()
    print("✋ Service stopped.")


@service.command("status")
def service_status(ctx: typer.Context) -> None:
    """Check service status"""
    ensure_root()
    ctx_obj = get_context_obj(ctx)
    service = ctx_obj.service
    status = service.status()
    print(f"🏃 Service status: {status}")
