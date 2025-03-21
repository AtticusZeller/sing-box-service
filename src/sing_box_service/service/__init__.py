import typer

from ..common import ensure_root
from .manager import LinuxServiceManager, WindowsServiceManager, create_service

__all__ = ["service", "WindowsServiceManager", "LinuxServiceManager", "create_service"]


service = typer.Typer(help="Service management commands")


@service.command("enable")
def service_enable(ctx: typer.Context) -> None:
    """Create sing-box service, enable autostart and start service"""
    ensure_root()
    config = ctx.obj.config
    service = create_service(config)
    service.create_service()
    service.start()
    print("🔥 Service started.")
    if config.api_base_url:
        print(f"🔌 Default API: {config.api_base_url}")


@service.command("disable")
def service_disable(ctx: typer.Context) -> None:
    """Stop service, disable sing-box service autostart and remove service"""
    ensure_root()
    config = ctx.obj.config
    service = create_service(config)
    service.stop()
    service.disable()
    print("✋ Autostart disabled.")


@service.command("restart")
def service_restart(ctx: typer.Context) -> None:
    """Restart sing-box service, update configuration if needed, create service if not exists"""
    ensure_root()
    config = ctx.obj.config
    service = create_service(config)
    if not service.check_service():
        service.create_service()
    if config.update_config():
        service.restart()
    else:
        print("❌ Failed to update configuration.")
        raise typer.Exit(1)
    print("🔥 Service restarted.")
    if config.api_base_url:
        print(f"🔌 Default API: {config.api_base_url}")


@service.command("stop")
def service_stop(ctx: typer.Context) -> None:
    """Stop sing-box service"""
    ensure_root()
    config = ctx.obj.config
    service = create_service(config)
    service.stop()
    print("✋ Service stopped.")


@service.command("status")
def service_status(ctx: typer.Context) -> None:
    """Check service status"""
    ensure_root()
    config = ctx.obj.config
    service = create_service(config)
    status = service.status()
    print(f"🏃 Service status: {status}")


@service.command("logs")
def service_logs(ctx: typer.Context) -> None:
    """Show sing-box service logs"""
    config = ctx.obj.config
    service = create_service(config)
    service.logs()
