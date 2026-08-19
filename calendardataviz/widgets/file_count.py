import datetime as dt
from collections.abc import Sequence
from pathlib import Path
from typing import Any, override

import TermTk as ttk
from ffcount import ffcount


class FileCountWidget(ttk.TTkFrame):
    """Widget that displays informations about the dataset's file count."""

    def __init__(
        self,
        target_nb_files: int,
        root_dir: Path,
        *args: Sequence[Any],
        **kwargs: dict[str, Any],
    ) -> None:
        """
        Args:
            target_nb_files: Allows to show a completion percentage.
            root_dir: Where to count files. Counts in this folder and
                all its sub folders.
            args: Arguments passed to the ttk.TTkWindow parent class.
            kwargs: Arguments passed to the ttk.TTkWindow parent class.
        """

        # Default values
        if "size" in kwargs:
            del kwargs["size"]
        if "border" in kwargs:
            del kwargs["border"]
        size = (len(str(f"{target_nb_files:_d}")) * 2 + 3, 5)
        super().__init__(size=size, border=False, *args, **kwargs)

        self._root_dir = root_dir
        self._target_nb_files = target_nb_files
        # Queue, number of files gained, date
        self._file_count_at_begining: int = ffcount(self._root_dir)[0]
        self._time_at_begining: dt.datetime = dt.datetime.now()

        # Spinner
        self._chars = r"-|"
        self._current_char = 0

        # Timer
        self._timer_duration = 4
        self._timer = ttk.TTkTimer()
        self._timer.timeout.connect(self._timer_update)
        self._timer.start(self._timer_duration)

    def _timer_update(self) -> None:
        self._current_char += 1
        if self._current_char == len(self._chars):
            self._current_char = 0
        self.update()
        self._timer.start(self._timer_duration)

    def _file_count(self) -> tuple[int, float]:
        # Compute files per minutes
        file_count = ffcount(self._root_dir)[0]
        files_gained = file_count - self._file_count_at_begining
        timedelta = dt.datetime.now() - self._time_at_begining
        files_per_minutes = files_gained / timedelta.total_seconds() * 60

        return file_count, files_per_minutes

    @override
    def paintEvent(self, canvas: ttk.TTkCanvas):
        """
        Paint Event callback.

        Args:
            canvas: The canvas object used to draw the widget.
        """

        super().paintEvent(canvas)
        file_count, files_per_minutes = self._file_count()
        completion_pct = file_count / self._target_nb_files * 100

        lines = [
            f"File count {self._chars[self._current_char]}",
            f"{file_count:_d} / {self._target_nb_files:_d}",
            f"{completion_pct:.2f}%",
            "Files/min",
            f"{files_per_minutes:.2f}",
        ]

        # Paint
        for i, line in enumerate(lines):
            canvas.drawText(
                pos=(0, i),
                text=line,
            )
