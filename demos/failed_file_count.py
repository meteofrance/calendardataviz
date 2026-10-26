"""Demo that shows how to display the number of files present in a
directory that correspond to each date.

The `FileCountInspector` is the only `InspectorABC` implementation
present in `calendardataviz` because it is the principal need this
library fulfills. You will probably need to implement your own
inspector, you should use it as a starting point.
"""

import datetime as dt
from pathlib import Path
from typing_extensions import override

from calendardataviz import start_app
from calendardataviz.colors import COOLWARM
from calendardataviz.file_count_inspector import FileCountInspector


class FailCountInspector(FileCountInspector):
    """Same as the File count Inspector, but parses
    fail message in .fail files.
    """

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

        # Define popup content wich will look like this:
        # file_path1.fail
        # Reason the file path failed
        #
        # file_path2.fail
        # ...
        content = ""
        for path in file_paths:
            content += path.name + "\n"
            with path.open("r") as file:
                lines = file.readlines()
            content += lines[4] + "\n"

        # Define Title
        title = (
            f"{date.strftime(r'%Y/%m/%d')} "
            f"({len(file_paths)}/{self.nb_expected_files_per_day})"
        )

        return title, content


if __name__ == "__main__":
    start_app(
        inspector=[
            FailCountInspector(
                name="Failed file count demo",
                root_dir=Path(__file__) / "demo_data",
                glob_pattern=r"**/%Y_%m_%d_*.fail",
                nb_expected_files_per_day=4,
                colors=COOLWARM,
            ),
            FileCountInspector(
                name="File count demo",
                root_dir=Path(__file__) / "demo_data",
                glob_pattern=r"**/%Y_%m_%d_*",
                nb_expected_files_per_day=4,
            ),
        ],
        years=[2026],
        nb_processes=1,
    )
