from collections.abc import Sequence
import datetime as dt
from multiprocessing import Queue
from multiprocessing.managers import SyncManager
from multiprocessing.pool import Pool
from multiprocessing.pool import Pool as PoolType
from traceback import format_exception

import TermTk as ttk
from typing_extensions import Any, override

from calendardataviz.inspector_abc import InspectorABC, RichString
from calendardataviz.widgets.calendar import CalendarWidget
from calendardataviz.widgets.colorbar import ColorBarWidget
from calendardataviz.widgets.loading_spinner import LoadingSpinnerWidget
from calendardataviz.widgets.popup import PopupWindowWidget

CURRENTLY_BEING_COMPUTED_COLOR = RichString(" ", bg_color="#000000", fg_color="#000000")
DEFAULT_DATE_COLOR = RichString(".", fg_color="#820782")
ERROR_DATE_COLOR = RichString("E", fg_color="#FF0000")


class ContainerSwitcher(ttk.TTkFrame):
    """Holds multiple CalendarContainerWidgets and allows to switch
    view between multiple containers.
    """

    def __init__(
        self,
        *,
        parent: ttk.TTkWidget,
        pos: tuple[int, int],
        inspectors: Sequence[InspectorABC],
        years: Sequence[int],
        manager: SyncManager,
        pool: PoolType,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            parent=parent,
            title="",
            pos=pos,
            size=(72, 9 * len(years) + 1),
            border=False,
            **kwargs,
        )

        self._containers: list[CalendarContainerWidget] = [
            CalendarContainerWidget(
                parent=self,
                inspector=inspector,
                years=years,
                pool=pool,
                manager=manager,
            )
            for inspector in inspectors
        ]
        self._current = 0
        self._containers[0].show()

    def switch_right(self) -> None:
        """Hides the currently shown calendar and show the next one."""
        self._containers[self._current].hide()
        self._current = (self._current + 1) % len(self._containers)
        self._containers[self._current].show()

    def switch_left(self) -> None:
        """Hides the currently shown calendar and show the previous one."""
        self._containers[self._current].hide()
        self._current = (self._current + len(self._containers) - 1) % len(self._containers)
        self._containers[self._current].show()

    def reload(self) -> None:
        """Reloads the calendar currently shown."""
        self._containers[self._current].reload()


class CalendarContainerWidget(ttk.TTkFrame):
    """Container that spawns for an inspector and a year list calendars and
    a color bar.
    """

    def __init__(
        self,
        *,
        parent: ttk.TTkWidget,
        inspector: InspectorABC,
        years: Sequence[int],
        manager: SyncManager,
        pool: PoolType,
        **kwargs: Any,
    ) -> None:

        super().__init__(
            parent=parent,
            pos=(0, 0),
            size=(72, 9 * len(years) + 1),
            title="",
            border=False,
            **kwargs,
        )

        # Color bar
        self.color_bar = ColorBarWidget(
            name=f"{inspector.name}_color_bar",
            inspector=inspector,
            parent=self,
            size=(6, 3 * 9 - 6),
            pos=(72, 6),
        )

        # Calendars
        self.calendars: list[CalendarWidget] = list()
        for i, year in enumerate(years):
            self.calendars.append(
                CalendarWidget(
                    inspector=inspector,
                    year=str(year),
                    queue=manager.Queue(),  # type: ignore[reportArgumentType]
                    pool=pool,
                    name=f"{inspector.name}_calendar_{year}",
                    parent=self,
                    pos=(0, i * 9),
                )
            )

        # Default behaviour is to be hidden
        self.hide()

    @override
    def show(self) -> None:
        """Starts calendar computations, show itself."""
        # for calendar in self.calendars:
        #     calendar.reload()

        super().show()

    @override
    def hide(self) -> None:
        """Stops calendar computations, show itself."""
        # for calendar in self.calendars:
            # calendar.stop_computation()
            # pass
        super().hide()

    def reload(self) -> None:
        for calendar in self.calendars:
            calendar.reload()