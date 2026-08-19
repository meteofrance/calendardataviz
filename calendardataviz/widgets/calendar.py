import datetime as dt
from multiprocessing import Queue
from multiprocessing.pool import Pool
from traceback import format_exception
from typing import Any, override

import TermTk as ttk

from calendardataviz.inspector_abc import InspectorABC, RichString
from calendardataviz.widgets.loading_spinner import LoadingSpinnerWidget
from calendardataviz.widgets.popup import PopupWindowWidget

CURRENTLY_BEING_COMPUTED_COLOR = ttk.TTkString(" ", ttk.TTkColor.BG_BLUE)
DEFAULT_DATE_COLOR = ttk.TTkString(".", ttk.TTkColor.fg("#820782"))
ERROR_DATE_COLOR = ttk.TTkString("E", ttk.TTkColor.fg("#FF0000"))


def _async_compute_date(
    args: tuple[
        InspectorABC,
        dt.date,
        "Queue[tuple[dt.date, RichString, bool]]",
    ],
) -> None:
    """Compute completion percentage and display color for one date.
    Uses queues to communicate to the associated calendar widget and
    file saving processes.

    Args:
        args:
            InspectorABC: A dataset inspector class.
            dt.datetime: The date for wich to compute.
            Queue: The calendar's queue.
    """

    inspector, date, calendar_queue = args

    # Split inputs and communicate to the calendar the start of computation
    calendar_queue.put((date, CURRENTLY_BEING_COMPUTED_COLOR, False))

    # Compute the completion percentage and display color for the given date
    try:
        ttk_string: ttk.TTkString = inspector.color_for_date(date)
    except Exception:
        calendar_queue.put((date, ERROR_DATE_COLOR, True))
        return

    # Send results to the calendar and file save process
    calendar_queue.put((date, ttk_string, True))


class CalendarWidget(ttk.TTkFrame):
    """Main widget of the app, displays informations for each dates
    in a given year. Allows to click on a dates.
    The information displayed is given by an inspector class
    that needs to be implemented once for each projects.
    """

    def __init__(
        self,
        inspector: InspectorABC,
        year: str,
        queue: "Queue[tuple[dt.date, ttk.TTkString, bool]]",
        pool: Pool,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Args:
            inspector: Inspector class associated with the dataset observed.
            year: Year this calendar will display.
            queue: Multiprocessing safe queue, used to communicate with
                async jobs computing completion percentages for a date.
            pool: Multiprocessing pool, used to start multiprocessing jobs.
            args: Arguments passed to the ttk.TTkWindow parent class.
            kwargs: Arguments passed to the ttk.TTkWindow parent class.
        """

        # Default values
        title: str = kwargs.get("title", f"{inspector.name} {year}")
        size: tuple[int, int] = kwargs.get("size", (71, 10))
        if "title" in kwargs:
            del kwargs["title"]
        if "size" in kwargs:
            del kwargs["size"]
        if "border" in kwargs:
            del kwargs["border"]
        super().__init__(title=title, size=size, border=True, *args, **kwargs)

        self.inspector = inspector
        self._year = year
        self.queue = queue
        self._pool = pool
        self._start_date = dt.date(int(year), 1, 1)
        self._end_date = dt.date(int(year) + 1, 1, 1) - dt.timedelta(days=1)
        self._x_offset = 5  # horizontal offset for drawing the calendar
        self._y_offset = 2  # vertical offset for drawing the calendar
        self._processing_dates: list[dt.date] = []
        self._nb_dates_in_processing_batch: int = 0

        # Associates a date to an onscreen position
        days_offset = int(self._start_date.strftime(r"%u")) - 1
        self._date_positions: dict[dt.date, tuple[int, int]] = {
            self._start_date + dt.timedelta(days=days): (
                (days + days_offset) // 7
                + (self._start_date + dt.timedelta(days=days)).month
                - 1
                + self._x_offset,
                (days + days_offset) % 7 + self._y_offset,
            )
            for days in range((self._end_date - self._start_date).days)
        }
        self._position_dates: dict[tuple[int, int], dt.date] = {
            value: key for key, value in self._date_positions.items()
        }

        # Initialise with a default color each date
        self._date_color: dict[dt.date, ttk.TTkString] = {
            date: DEFAULT_DATE_COLOR for date in self._position_dates.values()
        }

        # Initialize timer
        self._timer = ttk.TTkTimer()
        self._timer.timeout.connect(self._timer_update)
        self._timer.start(0.5)

        # Spawn loading widget
        self._spinner = LoadingSpinnerWidget(
            parent=self,
            pos=(0, 0),
            size=(1, 1),
            borders=False,
        )

        self._trigger_missing_dates_computing()

    def reload(self) -> None:
        """Reloads percentages for every dates."""
        self._date_color: dict[dt.date, ttk.TTkString] = {
            date: DEFAULT_DATE_COLOR for date in self._position_dates.values()
        }
        self._trigger_missing_dates_computing()

    def _trigger_missing_dates_computing(self) -> None:
        """Triggers multiprocessing jobs to compute missing dates."""
        # Find missing dates
        missing_dates: list[dt.date] = [
            date
            for date in self._date_positions
            if self._date_color[date] == DEFAULT_DATE_COLOR
        ]

        if len(missing_dates) != 0:
            self._processing_dates += missing_dates
            self._pool.imap_unordered(
                func=_async_compute_date,
                iterable={(self.inspector, date, self.queue) for date in missing_dates},
            )

            self._spinner.start()

    def _timer_update(self) -> None:
        """Method triggered by the calendar's update timer."""
        self.update(repaint=True)
        self._timer.start(1)

    @override
    def paintEvent(self, canvas: ttk.TTkCanvas) -> None:
        """
        Paint Event callback.

        Args:
            canvas: The canvas object used to draw the widget.
        """

        # Update values
        while not self.queue.empty():
            date, ttk_string, done = self.queue.get()
            self._date_color[date] = ttk_string

            if done:
                self._processing_dates.remove(date)

        if len(self._processing_dates) == 0:
            self._spinner.stop()

        super().paintEvent(canvas)

        # Paint y labels
        for i, day in enumerate(("mon", "tue", "wen", "thu", "fri", "sat", "sun")):
            canvas.drawText(
                pos=(self._x_offset - 4, self._y_offset + i),
                text=day,
            )

        # Paint values
        for date, (x, y) in self._date_positions.items():
            # Default values
            ttk_string = self._date_color[date]

            # Draw the date's cell
            canvas.drawTTkString((x, y), ttk_string)

            # Draw month name
            if date.day == 1:
                canvas.drawText(
                    text=date.strftime(r"%b"),
                    pos=(x + 1, self._y_offset - 1),
                )

    @override
    def mousePressEvent(self, evt: ttk.TTkMouseEvent) -> bool:
        """This event handler, can be reimplemented in a subclass
        to receive mouse press events for the widget.

        Args:
            evt: The mouse event

        Returns:
            bool: True if the event has been handled
        """

        # Check if event on date
        mouse_x, mouse_y = evt.pos()
        mouse_pos = (mouse_x, mouse_y)

        if mouse_pos not in self._date_positions.values():
            return False
        date = self._position_dates[mouse_pos]

        # Dont force recompute if value is already being computed
        if date in self._processing_dates:
            return True

        # Check if value already computed
        if date not in self._date_color:
            self._date_color[date] = self.inspector.color_for_date(date)

        # Get the description for the date, otherwise, format error
        try:
            popup_title, popup_content = self.inspector.popup_content(
                date=date,
            )
            if popup_content == "":
                popup_content = "vide"
        except Exception as e:
            popup_title = "ERROR"
            popup_content = "".join(format_exception(e))

        # Spawn a window
        PopupWindowWidget(
            text=popup_content,
            pos=(mouse_x, mouse_y + self.y()),
            parent=self._parent,
            title=popup_title,
        )

        return True
