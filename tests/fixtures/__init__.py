import re

import TermTk as ttk


def ansi_from_widget(widget: ttk.TTkWidget) -> str:
    canvas = ttk.TTkCanvas(
        width=widget.width(),
        height=widget.height(),
    )

    widget.paintEvent(canvas)

    return canvas.toAnsi()


def str_from_widget(widget: ttk.TTkWidget) -> str:
    # Regex patterns
    ansi_escape_sequence_pattern = re.compile(
        pattern=r"\x1b\[[0-9;]*[a-zA-Z]",
        flags=re.MULTILINE,
    )

    # Get ansi representation of the widget
    ansi = ansi_from_widget(widget)

    # Remove ansi escape sequences from the ansi representation
    re_match: re.Match[str]
    for re_match in sorted(
        ansi_escape_sequence_pattern.finditer(ansi),
        key=lambda x: x.start(0),
        reverse=True,
    ):
        ansi = ansi[: re_match.start(0)] + ansi[re_match.end(0) :]

    return ansi
