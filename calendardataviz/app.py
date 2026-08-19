"""Function `start_app` used to start the Terminal User Interface
to interact with one or multiple calendars.
"""

from collections.abc import Sequence
from multiprocessing import Manager, Pool
from multiprocessing.managers import SyncManager
from multiprocessing.pool import Pool as PoolType
from pathlib import Path

import TermTk as ttk

from calendardataviz.inspector_abc import InspectorABC
from calendardataviz.widgets.calendar import CalendarWidget
from calendardataviz.widgets.colorbar import ColorBarWidget
from calendardataviz.widgets.file_count import FileCountWidget


def _instantiate_widgets(
    manager: SyncManager,
    pool: PoolType,
    inspector: InspectorABC,
    years: Sequence[int],
    target_nb_files: int | None = None,
    root_dir: Path | None = None,
) -> ttk.TTk:
    """Instantiates and organises the app's widgets.

    Args:
        manager: Manager used to instantiate shared
            memory multiprocessing objects.
        pool: Pool of processes passed to the calendar
            widgets to instantiate their own processes.
        inspector: Inspector used by the calendars to display informations.
        years: Years for wich a calendar is spawned.
        target_nb_files: If given with `root_dir`, will spawn a
            file count widget.
        root_dir: If given with `target_nb_files`, will spawn a
            file count widget.

    Returns:
        ttk.TTk: Root widget.
    """

    # Root and scroll area
    root = ttk.TTk(name="root", layout=ttk.TTkLayout())
    scroll_area = ttk.TTkScrollArea(
        name="scroll_area",
        parent=root,
        pos=(0, 0),
        size=root.size(),
        visible=True,
        verticalScrollBarPolicy=ttk.TTkK.ScrollBarAlwaysOn,
    )

    # Color bar
    ColorBarWidget(
        name="color_bar",
        inspector=inspector,
        parent=scroll_area.viewport(),
        size=(6, 3 * 9 - 6),
        pos=(72, 6),
    )

    # Calendars
    calendars: list[CalendarWidget] = list()
    for i, year in enumerate(years):
        calendars.append(
            CalendarWidget(
                inspector=inspector,
                year=str(year),
                queue=manager.Queue(),
                pool=pool,
                name=f"calendar_{year}",
                parent=scroll_area.viewport(),
                pos=(0, i * 9),
            )
        )

    # Might spawn a FileCountWidget
    if target_nb_files and root_dir:
        FileCountWidget(
            name="file_count",
            parent=scroll_area.viewport(),
            pos=(71, 0),
            target_nb_files=target_nb_files,
            root_dir=root_dir,
        )

    # Quit button
    quit_button = ttk.TTkButton(
        name="quit_button",
        parent=scroll_area.viewport(),
        pos=(0, 0),
        text="quit",
    )
    quit_button.clicked.connect(ttk.TTkHelper.quit)

    # Reload button
    reload_button = ttk.TTkButton(
        name="reload_button",
        parent=scroll_area.viewport(),
        pos=(6, 0),
        text="🔄️",
    )
    for calendar in calendars:
        reload_button.clicked.connect(calendar.reload)

    return root


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

    with Manager() as manager, Pool(processes=nb_processes) as pool:
        root = _instantiate_widgets(
            manager=manager,
            pool=pool,
            inspector=inspector_cls(),
            years=years,
            target_nb_files=target_nb_files,
            root_dir=root_dir,
        )

        root.mainloop()
        pool.close()
        pool.join()
