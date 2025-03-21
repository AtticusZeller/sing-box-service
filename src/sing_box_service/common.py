import os
from enum import Enum

StrOrNone = str | None


class LogLevel(str, Enum):
    trace = "trace"
    debug = "debug"
    info = "info"
    warning = "warning"
    error = "error"
    fatal = "fatal"
    panic = "panic"


def ensure_root() -> None:
    """https://gist.github.com/RDCH106/fdd419ef7dd803932b16056aab1d2300"""
    try:
        if os.geteuid() != 0:  # type: ignore
            raise SystemError("⚠️ This script must be run as root.")
    except AttributeError:
        import ctypes

        if not ctypes.windll.shell32.IsUserAnAdmin():  # type: ignore
            raise SystemError("⚠️ This script must be run as Administrator.")
