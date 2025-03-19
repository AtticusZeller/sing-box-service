from collections.abc import Generator
from io import StringIO
from typing import Any

from prompt_toolkit import ANSI
from prompt_toolkit.formatted_text import FormattedText, to_formatted_text
from rich import box
from rich.ansi import AnsiDecoder
from rich.console import Console, Group
from rich.jupyter import JupyterMixin
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


class RichPlotMixin(JupyterMixin):
    """A Rich-compatible plot using plotext."""

    def __init__(self) -> None:
        super().__init__()
        # For Rich rendering
        self.decoder = AnsiDecoder()

    def make_plot(self, width: int, height: int) -> str:
        raise NotImplementedError

    def __rich_console__(self, console, options) -> Generator[Group | str, Any, None]:  # type: ignore[no-untyped-def]
        """
        Render the graph as a Rich console renderable.
        Ref: https://github.com/piccolomo/plotext/blob/master/readme/environments.md#rich
        Args:
            console: The Rich console
            options: Console options including width and height

        Yields:
            Rich-compatible renderables
        """
        # Adapt to the available width and height
        width = options.max_width or console.width
        height = options.height or console.height
        # Build the plot and convert to Rich format
        try:
            canvas = self.make_plot(width, height)
            yield Group(*self.decoder.decode(canvas))
        except Exception as e:
            yield f"Error rendering graph: {str(e)}"
