"""Demo that shows how to display the number of files present in a
directory that correspond to each date.

The `FileCountInspector` is the only `InspectorABC` implementation
present in `calendardataviz` because it is the principal need this
library fulfills. You will probably need to implement your own
inspector, you should use it as a starting point.
"""

from pathlib import Path

from calendardataviz import start_app
from calendardataviz.file_count_inspector import FileCountInspector

if __name__ == "__main__":
    start_app(
        inspector=[
            FileCountInspector(
                name="File count demo",
                root_dir=Path("demos/demo_data"),
                glob_pattern=r"**/%Y_%m_%d_*",
                nb_expected_files_per_day=4,
            ),
        ],
        years=[2026],
        nb_processes=1,
    )
