import datetime as dt
from abc import ABC, abstractmethod
from pathlib import Path

from calendardataviz.rich_string import RichString


class InspectorABC(ABC):
    """Abstract base class used by the calendar widget
    to get display values.
    """

    name: str  # Name displayed atop the calendar
    root_dir: Path

    @abstractmethod
    def color_for_date(self, date: dt.date) -> RichString:
        """Returns the color for a given date.

        Args:
            date: date.

        Returns:
            RichString: The text and color associated
                to the given date.
        """
        raise NotImplementedError

    @abstractmethod
    def as_color_bar(self, size: int) -> list[RichString]:
        """Returns values for a color bar of the given size.

        Args:
            size: Size of the colorbar to generate.

        Returns:
            list[RichString]: A list of length "size"
                containing one character RichStrings, one
                for each cell of the color bar.
        """
        raise NotImplementedError

    @abstractmethod
    def popup_content(self, date: dt.date) -> tuple[str, str]:
        """Return the information displayed when a date is selected.

        Args:
            date: Date selected.

        Returns:
            str: The pop-up window title.
            str: The pop-up window content.
        """
        raise NotImplementedError
