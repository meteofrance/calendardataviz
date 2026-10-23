import datetime as dt
from typing import override

from calendardataviz import InspectorABC, RichString, start_app
from calendardataviz.colors import RDYLGN, color_bar, color_from_pct


class YourInspector(InspectorABC):
    """Your inspector to implement."""

    name = "my inspector"

    @override
    def color_for_date(self, date: dt.date) -> RichString:
        """Returns the color for a given date.

        Args:
            date: date.

        Returns:
            RichString: The text and color associated
                to the given date.
        """

        # return RichString(" ", bg_color="#9032C2")
        return color_from_pct(date.day / 31, RDYLGN)

    @override
    def as_color_bar(
        self, size: int
    ) -> list[RichString] | tuple[list[RichString], list[str]]:
        """Returns values for a color bar of the given size.

        Args:
            size: Size of the colorbar to generate.

        Returns:
            list[RichString]: A list of length "size"
                containing one character TTkStrings, one
                for each cell of the color bar.
        """

        # return [RichString(" ", bg_color="#9032C2")] * size, ["-"] * size
        return color_bar(size, RDYLGN)

    @override
    def popup_content(self, date: dt.date) -> tuple[str, str]:
        """Return the information displayed when a date is selected.

        Args:
            date: Date selected.

        Returns:
            str: The pop-up window title.
            str: The pop-up window content.
        """

        return f"Popup Title {date}", "Popup Content"


if __name__ == "__main__":
    start_app(
        inspector=YourInspector(),
        years=[2024, 2025],
        nb_processes=1,
    )
