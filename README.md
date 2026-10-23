# Calendar Data Visualisation
Terminal interface to visualise calendar data.

**Features**:
- 📆 Terminal calendar view that colors each day according to your data.
- 🔍 Click any date to reveal a popup with its details.
- Multiple calendars in a single app.
- Ready-to-use color bar and file count widgets.
- 🌈 Color maps to get you started, plus a built-in `FileCountInspector` you can
  reuse or subclass for your own dataset.
- ⚡ Multiprocessing computing to speed up calendar initialisation on large datasets.
- 🐛 Easy to debug, stack traces are shown in the UI instead of failing silently.
- 🚀 Adapt it to your data by implementing a single [`InspectorABC`](https://github.com/meteofrance/calendardataviz/blob/main/calendardataviz/inspector_abc.py) class.

![](https://github.com/meteofrance/calendardataviz/blob/main/doc/images/calendar_data_vizualisation.png?raw=true)
_Calendar implemented to show the the number of files present for each dates of the years 2024, 2025 and 2026, with a popup showing informations for the date 10/10/2025_

## Install
This package is available on pypi. Install with your prefered package manager.

```sh
pip install calendardataviz
# or
uv add calendardataviz
```

## Startup guide
In your project, create a script and copy in it one of the following demos.

Edit the code to fit your needs, then run it to see your calendar.


### [File count demo](https://github.com/meteofrance/calendardataviz/blob/main/demos/file_count.py)
![Calendar showing the number of files present for each day of the year 2026](https://github.com/meteofrance/calendardataviz/blob/main/doc/images/file_count.png?raw=true)

```py
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
```


### [Customise the file count demo](https://github.com/meteofrance/calendardataviz/blob/main/demos/failed_file_count.py)
![Calendar showing the number of files that failed for each day of the year 2026](https://github.com/meteofrance/calendardataviz/blob/main/doc/images/failed_file_count.png?raw=true)

You will probably need to customise the `FileCountInspector` to display informations about your own dataset. This demo shows how to surcharge one of its functions.

It also shows that you can give multiple inspectors to the `start_app` method and you are able to switch between them in the interface using the buttons at the top of the terminal.

To fully control the file count calendar, you are encouraged to reimplement it as your own by copying [its source code](https://github.com/meteofrance/calendardataviz/blob/main/calendardataviz/file_count_inspector?raw=true)


### [Code template](https://github.com/meteofrance/calendardataviz/blob/main/demos/code_template.py)
![Calendar that shows only purple](https://github.com/meteofrance/calendardataviz/blob/main/doc/images/code_template.png?raw=true)

Other wise, start from scratch by using the bare code template.

### [Color bars demo](https://github.com/meteofrance/calendardataviz/blob/main/demos/color_bars.py)
![Calendar with a different color for each day to form a rainbow](https://github.com/meteofrance/calendardataviz/blob/main/doc/images/color_bars.png?raw=true)

Not much use as a code template, but useful to see the color bars available in `calendardataviz.colors`.


---


## References

Here is a presentation of the different classes and functions you need to know to implement your own inspector.


### `InspectorABC`
Abstract base class you need to implement. It has 3 method to override:
- `color_for_date` wich returns the color for a given date.
- `as_color_bar` wich returns values for a color bar of a given size.
- `popup_content` wich returns content for the popup displayed when
    the user clicks on a date.


### `RichString`
A class used to define a background and foreground color along side a string. This string representation is expected to be returned by your implementation of the `InspectorABC` class.

```py
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
```

### `start_app`
Entry point for the app, starts the Terminal User Interface.

```py
def start_app(
    inspector: InspectorABC | Sequence[InspectorABC],
    years: Sequence[int],
    nb_processes: int = 1,
    target_nb_files: int | None = None,
    root_dir: Path | None = None,
) -> None:
    """Library entry point, instantiates and starts the terminal interface.
    If target_nb_files and root_dir are given, also spawns a file count
    widget, wich displays informations about the file count and the
    completion percentage (nb of files in root dir / target_nb_files).

    Args:
        inspector: Your project's implementation of the
            `calendardataviz.InspectorABC`. This is the class
            used by the app to get information for each dates.
        years: A sequence of years. A calendar will be displayed
            for each year.
        nb_processes: Number of multiprocessing processes to use.
            If your inspector's `color_for_date` method is not
            instantaneous, helps speed up the calendar's initialisation.
        target_nb_files: If given with `root_dir`, will spawn a
            file count widget.
        root_dir: If given with `target_nb_files`, will spawn a
            file count widget.
    """
```


### Default colors for color bar
You can use color bars shipped with `calendardataviz`.
For exemple, here is the implementation of the `color_for_date` function of the `InspectorABC` class for the [rainbow demo](#demos).

```py
import datetime as dt
from typing import override

from calendardataviz import InspectorABC, RichString, start_app
from calendardataviz.colors import RAINBOW, color_from_pct, color_bar


class RainbowInspector(InspectorABC):
    # ...

    @override
    def color_for_date(self, date: dt.date) -> RichString:
        """Returns the color for a given date.

        Args:
            date: date.

        Returns:
            RichString: The text and color associated
                to the given date.
        """

        # Compute a completion percentage for the given date
        pct =  # float value between 0 and 1

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

        return color_bar(size, RAINBOW)
```

You can see that this implementation of the `InspectorABC` uses the `calendardataviz.colors.RAINBOW` color bar and uses the `calendardataviz.colors.color_from_pct` function to sample it.


---


# Contribution
Please contribute by proposing a merger request.

You can install the project in development mode like so:
```sh
git clone https://github.com/meteofrance/calendardataviz.git
cd calendardataviz
uv sync --all-extras
```

To format then test your code:
```
uvx ruff format
uvx ruff check --fix
uv run pyright
uv run pytest -s
```

Once your code is formated and tested, you can create a merge request
of your branch into the main branch.
