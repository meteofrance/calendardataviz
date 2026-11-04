"""Function `start_app` used to start the Terminal User Interface
to interact with one or multiple calendars.
"""

from collections.abc import Sequence
from multiprocessing import Manager, Pool
from multiprocessing.managers import SyncManager
from multiprocessing.pool import Pool as PoolType

import TermTk as ttk

from calendardataviz.inspector_abc import InspectorABC
from calendardataviz.widgets.calendar_container import ContainerSwitcher


def _instantiate_widgets(
    manager: SyncManager,
    pool: PoolType,
    inspectors: InspectorABC | Sequence[InspectorABC],
    years: Sequence[int],
) -> ttk.TTk:
    """Instantiates and organises the app's widgets.

    Args:
        manager: Manager used to instantiate shared
            memory multiprocessing objects.
        pool: Pool of processes passed to the calendar
            widgets to instantiate their own processes.
        inspectors: One or more inspectors used by the
            calendars to display informations.
        years: Years for wich a calendar is spawned.

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

    # Container switcher wich contains multiple calendars and allows to switch
    # between them.
    inspectors = inspectors if isinstance(inspectors, Sequence) else [inspectors]
    container_switcher = ContainerSwitcher(
        parent=scroll_area.viewport(),
        pos=(0, 1),
        inspectors=inspectors,
        years=years,
        pool=pool,
        manager=manager,
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
        text="⟲",
    )
    reload_button.clicked.connect(container_switcher.reload)

    # Switch buttons
    switch_left = ttk.TTkButton(
        name="switch_left_button",
        parent=scroll_area.viewport(),
        pos=(9, 0),
        text="◀",
    )
    switch_right = ttk.TTkButton(
        name="switch_right_button",
        parent=scroll_area.viewport(),
        pos=(12, 0),
        text="▶",
    )
    switch_left.clicked.connect(container_switcher.switch_left)
    switch_right.clicked.connect(container_switcher.switch_right)

    return root


def start_app(
    inspector: InspectorABC | Sequence[InspectorABC],
    years: Sequence[int],
    nb_processes: int = 1,
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
    """

    with Manager() as manager, Pool(processes=nb_processes) as pool:
        root = _instantiate_widgets(
            manager=manager,
            pool=pool,
            inspectors=inspector,
            years=years,
        )

        root.mainloop()
        pool.close()
        pool.join()
