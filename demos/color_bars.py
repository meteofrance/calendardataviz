"""Demonstration of an app that shows multiple calendars,
one for each of the inspectors given.

Also shows the ability to switch between multiple inspectors
passed to the start app methode, using the "◀" and "▶" buttons
at the top of the interface.
"""

import datetime as dt

from typing_extensions import override

from calendardataviz import InspectorABC, RichString, start_app
from calendardataviz.colors import color_bar, color_bar_registry, color_from_pct


class RainbowInspector(InspectorABC):
    """Implementation of the InspectorABC class for
    demonstration purposses. Attributes a color to
    each date to create a rainbow pattern.
    """

    def __init__(self, name: str, color_bar: list[RichString]) -> None:
        """
        Args:
            name: Name of the inspector.
            color_bar: Colors used to display the rainbow.
        """
        self.name = name
        self.colors = color_bar

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
        return color_from_pct(pct, self.colors)

    @override
    def as_color_bar(self, size: int) -> tuple[list[RichString], list[str]]:
        """Returns values for a color bar of the given size.

        Args:
            size: Size of the colorbar to generate.

        Returns:
            list[RichString]: A list of length "size"
                containing one character RichStrings, one
                for each cell of the color bar.
            list[str]: A list of string of length "size",
                displayed by the color bar widget as labels.
        """

        return color_bar(size, self.colors)

    @override
    def popup_content(self, date: dt.date) -> tuple[str, RichString]:
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
        content = RichString(
            text=f"#{hex(r)[2:]}{hex(g)[2:]}{hex(b)[2:]}\n",
        ) + RichString(
            text="\n".join([" " * 15] * 10),
            bg_color=(r, g, b),
        )

        return title, content


if __name__ == "__main__":
    start_app(
        inspector=[
            RainbowInspector(name, colorbar)
            for name, colorbar in color_bar_registry.items()
        ],
        years=[2024, 2025, 2026],
        nb_processes=1,
    )
