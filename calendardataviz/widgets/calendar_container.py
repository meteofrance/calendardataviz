from collections.abc import Sequence
from multiprocessing.managers import SyncManager
from multiprocessing.pool import Pool as PoolType

import TermTk as ttk
from typing_extensions import Any, override

from calendardataviz.inspector_abc import InspectorABC, RichString
from calendardataviz.widgets.calendar import CalendarWidget
from calendardataviz.widgets.colorbar import ColorBarWidget

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
        inspectors: Sequence[InspectorABC],
        years: Sequence[int],
        manager: SyncManager,
        pool: PoolType,
        **kwargs: Any,
    ) -> None:
        """
        Args:
            inspectors: One or more inspectors used by the
                calendars to display informations.
            years: Years for wich a calendar is spawned.
            manager: Manager used to instantiate shared
                memory multiprocessing objects.
            pool: Pool of processes passed to the calendar
                widgets to instantiate their own processes.
            kwargs: Arguments passed to the ttk.TTkFrame init method.
        """

        super().__init__(
            title="",
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
        self._current = (self._current + len(self._containers) - 1) % len(
            self._containers
        )
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
        inspector: InspectorABC,
        years: Sequence[int],
        manager: SyncManager,
        pool: PoolType,
        **kwargs: Any,
    ) -> None:
        """
        Args:
            inspector: Inspectors used by the calendars to display informations.
            years: Years for wich a calendar is spawned.
            manager: Manager used to instantiate shared
                memory multiprocessing objects.
            pool: Pool of processes passed to the calendar
                widgets to instantiate their own processes.
            kwargs: Arguments passed to the ttk.TTkFrame init method.
        """

        super().__init__(
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
        """Reloads all calendars."""
        for calendar in self.calendars:
            calendar.reload()
