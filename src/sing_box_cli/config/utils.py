import json
from pathlib import Path
from typing import Any

import httpx
from rich import print


def show_diff_config(current_config: str, new_config: str) -> None:
    print("📄 Configuration differences:")
    from difflib import unified_diff

    diff = list(
        unified_diff(
            current_config.splitlines(),
            new_config.splitlines(),
            fromfile="old",
            tofile="new",
            lineterm="",
        )
    )

    for line in diff:
        if line.startswith("+"):
            print(f"[green]{line}[/green]")
        elif line.startswith("-"):
            print(f"[red]{line}[/red]")
        elif line.startswith("@@"):
            print(f"[blue]{line}[/blue]")
        elif line.startswith(("---", "+++")):
            print(f"[dim]{line}[/dim]")
        else:
            print(f"[white]{line}[/white]")


def check_url(url: str) -> bool:
    try:
        response = httpx.head(url)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ Invalid URL: {e}")
        return False


def load_json_config(config_file: Path) -> dict[str, Any]:
    try:
        return dict(json.loads(config_file.read_text(encoding="utf-8")))
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return {}
