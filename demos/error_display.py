"""Demonstration of error display capabilities."""

import datetime as dt
from typing_extensions import override

from calendardataviz import InspectorABC, RichString, start_app


class InspectorThatRaisesErrors(InspectorABC):
    """Implementation of the InspectorABC class that
    raises errors.
    """

    name = "Inspector that raises errors"

    @override
    def color_for_date(self, date: dt.date) -> RichString:
        """Returns the color for a given date."""

        raise ValueError(
            "Error in the color_for_date function of the InspectorThatRaisesErrors "
            "class.\n The error stack trace is displayed at the top of the "
            "popup content."
        )

    @override
    def as_color_bar(self, size: int) -> tuple[list[RichString], list[str]]:
        """Returns values for a color bar of the given size."""
        # Define colors for the color bar, following a rainbow patterm
        color_bar = [
            RichString(" ") for _ in range(size + 1)
        ]

        # Define labels
        labels = [""] * (size + 1)

        return color_bar, labels
    

    @override
    def popup_content(self, date: dt.date) -> tuple[str, RichString]:
        """Return the information displayed when a date is selected."""

        raise ValueError(
            "Error in the popup_content function of the InspectorThatRaisesErrors "
            "class.\n The error stack trace is displayed in place of the "
            "popup content."
        )


if __name__ == "__main__":
    start_app(
        inspector=InspectorThatRaisesErrors(),
        years=[2024, 2025],
        nb_processes=1,
    )
