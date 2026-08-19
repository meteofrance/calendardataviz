"""Demonstration of a rainbow calendar.
Shows how to implement an `InspectorABC`
class and run the Terminal User Interface
to interact with it.
"""

import datetime as dt
from typing import override

from calendardataviz import InspectorABC, RichString, start_app


def float_to_rgb(x: float) -> tuple[int, int, int]:
    """Map a float in [0, 1] to a RGB color from a color bar.

    Args:
        x: Value to be mapped to rgb. Should be contained in [0, 1].

    Return:
        tuple[int, int, int]: RGB value mapped from the given float.
    """
    # Clamp
    x = max(0.0, min(1.0, x))

    # Defines anchor colors and their positions in the [0, 1] interval
    anchors = [0.0, 0.25, 0.5, 0.75, 1.0]
    colors = [
        (0, 0, 255),  # blue
        (0, 255, 255),  # cyan
        (0, 255, 0),  # green
        (255, 255, 0),  # yellow
        (255, 0, 0),  # red
    ]

    # Find the interval that contains x
    for i in range(len(anchors) - 1):
        if not (anchors[i] <= x <= anchors[i + 1]):
            continue
        # Interpolate between the two anchor values
        interpolation_factor = (x - anchors[i]) / (anchors[i + 1] - anchors[i])
        r1, g1, b1 = colors[i]
        r2, g2, b2 = colors[i + 1]
        r = int(r1 + (r2 - r1) * interpolation_factor)
        g = int(g1 + (g2 - g1) * interpolation_factor)
        b = int(b1 + (b2 - b1) * interpolation_factor)
        return (r, g, b)

    # Default color (should never be reached)
    return (255, 0, 255)


class RainbowInspector(InspectorABC):
    """Implementation of the InspectorABC class for
    demonstration purposses. Attributes a color to
    each date to create a rainbow pattern.
    """

    name = "Rainbow"

    @override
    def color_for_date(self, date: dt.date) -> RichString:
        """Returns the color for a given date.

        Args:
            date: date.

        Returns:
            RichString: The text and color associated
                to the given date.
        """

        # Compute the number of the day from the start of the year
        day_nb = (date - dt.date(date.year, 1, 1)).days

        # Compute the total number of days in the year
        nb_days_in_year = (dt.date(date.year + 1, 1, 1) - dt.date(date.year, 1, 1)).days

        # Compute the position of the day in the year as a percentage
        pct = day_nb / nb_days_in_year

        # Return a rich string with a background color from a color map
        return RichString(
            text=" ",
            bg_color=float_to_rgb(pct),
        )

    @override
    def as_color_bar(self, size: int) -> list[RichString]:
        """Returns values for a color bar of the given size.

        Args:
            size: Size of the colorbar to generate.

        Returns:
            list[RichString]: A list of length "size"
                containing one character TTkStrings, one
                for each cell of the color bar.
        """

        return [
            RichString(
                text=" ",
                bg_color=float_to_rgb(pct),
            )
            for pct in [i / size for i in range(size + 1)]
        ]

    @override
    def popup_content(self, date: dt.date) -> tuple[str, str]:
        """Return the information displayed when a date is selected.

        Args:
            date: Date selected.

        Returns:
            str: The pop-up window title.
            str: The pop-up window content.
        """

        date_string = self.color_for_date(date)
        r, g, b = date_string.colorAt(0).bgToRGB()
        title = date.strftime(r"%A %d %B %Y")
        content = f"#{hex(r)[2:]}{hex(g)[2:]}{hex(b)[2:]}  "

        return title, content


if __name__ == "__main__":
    start_app(
        inspector_cls=RainbowInspector,
        years=[2024, 2025, 2026],
        nb_processes=1,
    )
