"""Inspector that displays the number of files present in a
directory that correspond to each date.

The `FileCountInspector` is the only `InspectorABC` implementation
present in `calendardataviz` because it is the principal need this
library fulfills. You will probably need to implement your own
inspector, you should use it as a starting point.
"""

import datetime as dt
from pathlib import Path
from typing import override

from calendardataviz import InspectorABC, RichString
from calendardataviz.colors import RDYLGN, color_bar, color_from_pct


class FileCountInspector(InspectorABC):
    """Inspector that counts the number of files present for
    each dates in the demos/demo_data folder.
    """

    def __init__(
        self,
        name: str,
        root_dir: Path,
        glob_pattern: str,
        nb_expected_files_per_day: int,
        colors: list[RichString] = RDYLGN,
    ) -> None:
        """
        Args:
            name: The calendar's display name.
            root_dir: Root directory of the inspected files.
            glob_pattern: `datetime.date.strftime` pattern used as a glob
                pattern to find files in the root directory.
                Example: "**/%Y_%m_%d_*.txt", will match in any sub
                directories files with name like "year_month_day_*.txt"
            nb_expected_files_per_day: How many files are expected to be found
                for a date, used as denominator in date completion percentage
                and color computation.
            colors: Wich color map to use as color bar.
        """

        self.name = name
        self.root_dir = root_dir
        self.glob_pattern = glob_pattern
        self.nb_expected_files_per_day = nb_expected_files_per_day
        self.colors = colors

    def _files_for_date(self, date: dt.date) -> list[Path]:
        """Return all files belonging to the given date.

        Uses a glob pattern matching the date prefix (YYYY_MM_DD_) anywhere
        under the inspector's root_dir.

        Args:
            date: Date to look up.

        Returns:
            list[Path]: The files matching the date prefix.
        """
        return list(self.root_dir.glob(date.strftime(self.glob_pattern)))

    @override
    def color_for_date(self, date: dt.date) -> RichString:
        """Returns the color for a given date.

        Args:
            date: date.

        Returns:
            RichString: The text and color associated
                to the given date.
        """
        pct = len(self._files_for_date(date)) / self.nb_expected_files_per_day
        return color_from_pct(pct, self.colors)

    @override
    def as_color_bar(self, size: int) -> tuple[list[RichString], list[str]]:
        """Returns values for a color bar of the given size.

        Args:
            size: Size of the color bar to generate.

        Returns:
            list[RichString]: A list of length "size"
                containing one character TTkStrings, one
                for each cell of the color bar.
            list[str]: A list of length "size" containing
                a label for each cell of the color bar.
        """
        return color_bar(size=size, colors=self.colors)

    @override
    def popup_content(self, date: dt.date) -> tuple[str, str]:
        """Return the information displayed when a date is selected.

        Args:
            date: Date selected.

        Returns:
            str: The pop-up window title.
            str: The pop-up window content.
        """

        file_paths = sorted(self._files_for_date(date))
        content = "\n".join(path.name for path in file_paths)
        title = (
            f"{date.strftime(r'%Y/%m/%d')} "
            f"({len(file_paths)}/{self.nb_expected_files_per_day})"
        )

        return title, content
