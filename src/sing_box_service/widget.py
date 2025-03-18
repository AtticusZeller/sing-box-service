from io import StringIO
from typing import Any

from prompt_toolkit import ANSI
from prompt_toolkit.formatted_text import FormattedText, to_formatted_text
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


def create_header_panel(title: str) -> Panel:
    return Panel(
        Text(title, justify="center"), style="bold white on bright_blue", box=box.SIMPLE
    )


def render_rich_to_prompt_toolkit(rich_obj: Any) -> FormattedText:
    """Convert a Rich object to prompt_toolkit formatted text."""
    # Capture rich output as string
    console = Console(
        file=StringIO(), color_system="truecolor", highlight=True, force_terminal=True
    )
    console.print(rich_obj)
    output = console.file.getvalue()  # type: ignore

    # Convert to prompt_toolkit formatted text
    return to_formatted_text(ANSI(output))
