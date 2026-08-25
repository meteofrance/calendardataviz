"""Demonstration of a rainbow calendar.
Shows how to implement an `InspectorABC`
class and run the Terminal User Interface
to interact with it.
"""

import datetime as dt
from typing import override

from calendardataviz import InspectorABC, RichString, start_app
from calendardataviz.colors import RAINBOW, color_from_pct


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
        return color_from_pct(pct, RAINBOW)

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

        # Define colors for the color bar, following a rainbow patterm
        color_bar = [
            color_from_pct(pct, RAINBOW) for pct in [i / size for i in range(size + 1)]
        ]

        # Define labels each 5 steps of the color bar
        labels = []
        for i, char in enumerate(color_bar):
            if i % 5 == 0 or i == len(color_bar) - 1:
                r, g, b = char.colorAt(0).bgToRGB()
                labels.append(f"#{hex(r)[2:]}{hex(g)[2:]}{hex(b)[2:]}  ")
            labels.append("")

        return color_bar, labels

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
