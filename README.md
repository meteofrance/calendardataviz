# Calendar Data Visualisation
Terminal interface to visualise calendar data.

![](doc/images/calendar_data_vizualisation.png)

## Install
This package is available on pypi. Install with your prefered package manager.

```sh
pip install calendardataviz
# or
uv add calendardataviz
```

## Usage
In your project, create a script that implements the `InspectorABC` class
make it return `RichString` class instances then call the `start_app`
function. You can read our demos in available in the [demos]() folder.
Here is a presentation of the different classes and functions:

### `RichString`
A class used to define a background and foreground color along side a string.

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

### `InspectorABC`
Abstract base class you need to implement. It has 3 method to override:
- `color_for_date` wich returns the color for a given date.
- `as_color_bar` wich returns values for a color bar of a given size.
- `popup_content` wich returns content for the popup displayed when
    the user clicks on a date.

Described in more details in the script template available bellow.

### `start_app`
Entry point for the app, starts the Terminal User Interface.

```py
def start_app(
    inspector_cls: type[InspectorABC],
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
        inspector_cls: Your project's implementatino of the
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

### Script template

Here is a script template you can copy to start your own implementation
of the `InspectorABC` class.

```python
"""Demonstration of a rainbow calendar.
Shows how to implement an `InspectorABC`
class and run the Terminal User Interface
to interact with it.
"""

import datetime as dt
from typing import override

from calendardataviz import InspectorABC, RichString, start_app


class YourInspector(InspectorABC):
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
        pass

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
        pass

    @override
    def popup_content(self, date: dt.date) -> tuple[str, str]:
        """Return the information displayed when a date is selected.

        Args:
            date: Date selected.

        Returns:
            str: The pop-up window title.
            str: The pop-up window content.
        """
        pass


if __name__ == "__main__":
    start_app(
        inspector_cls=YourInspector,
        years=[2024, 2025, 2026],
        nb_processes=1,
    )
```

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
uv run pytest -s
```

Once your code is formated and tested, you can create a merge request
of your branch into the main branch.
