import re

import TermTk as ttk


def _convert_color_input(
    color: str | tuple[int, int, int] | tuple[float, float, float],
) -> tuple[int, int, int]:
    """Tries to convert a user inputed string to 255 values rgb.
    Raises a value error if no accepted format is recognised
    in the input.

    Args:
        color: Color representation, accepted formats are:
            - An string hexadecimal representation (`#ff00ff`, `ff00ff`)"
            - A tuple of int rgb values (255, 0, 255)"
            - A tuple of float rgb values (1.0, 0.0, 1.0)"

    Returns:
        tuple[int, int, int]: 255 values rgb representation of a color.
    """
    error = ValueError(
        "Color values are expected to be given as:\n"
        "- An string hexadecimal representation (`#ff00ff`, `ff00ff`)\n"
        "- A tuple of int rgb values (255, 0, 255)\n"
        "- A tuple of float rgb values (1.0, 0.0, 1.0)\n"
        f"Received {color} of type {type(color)}."
    )

    if isinstance(color, tuple):
        r, g, b = color
        if all(isinstance(value, int) for value in color) and all(
            0 <= value <= 255 for value in color
        ):
            return int(r), int(g), int(b)
        if all(isinstance(value, float) for value in color) and all(
            0 <= value <= 1 for value in color
        ):
            return int(r * 255), int(g * 255), int(b * 255)

    if isinstance(color, str):
        re_match: re.Match[str] | None = re.search(
            pattern=(
                r"#?"
                r"(?P<r>[0-9a-fA-F]{2})"
                r"(?P<g>[0-9a-fA-F]{2})"
                r"(?P<b>[0-9a-fA-F]{2})"
            ),
            string=color,
        )
        if (
            re_match is None
            or re_match.group("r") is None
            or re_match.group("g") is None
            or re_match.group("b") is None
        ):
            raise error

        return (
            int(re_match.group("r"), 16),
            int(re_match.group("g"), 16),
            int(re_match.group("b"), 16),
        )

    raise error


class RichString(ttk.TTkString):
    """String class offering the possiblity to define a
    background and foreground color along a string.

    In practice, is an easy to use interface for the
    TermTk.TTkString class, and only override its init method.
    """

    def __init__(
        self,
        text: str,
        bg_color: str | tuple[int, int, int] | tuple[float, float, float] = "#000000",
        fg_color: str | tuple[int, int, int] | tuple[float, float, float] = "#ffffff",
    ) -> None:
        """
        Args:
            text: Text.
            bg_color: Background color, either as an hexadecimal value
                such as `#ff00ff` or as a tuple of values, `(255, 0, 255)`.
            fg_color: Foreground color, in the same format as bg_color.
        """
        super().__init__(
            text=text,
            color=ttk.TTkColor(
                fg=_convert_color_input(fg_color),
                bg=_convert_color_input(bg_color),
            ),
        )

RichStringType = str | RichString | ttk.TTkString