from collections.abc import Sequence
from typing import Any, override

import TermTk as ttk


class LoadingSpinnerWidget(ttk.TTkFrame):
    """Loading widget, with a loading spinner"""

    def __init__(self, *args: Sequence[Any], **kwargs: dict[str, Any]) -> None:
        """
        Args:
            args: Arguments passed to the ttk.TTkWindow parent class.
            kwargs: Arguments passed to the ttk.TTkWindow parent class.
        """

        # Default values
        if "size" in kwargs:
            del kwargs["size"]
        if "borders" in kwargs:
            del kwargs["borders"]
        super().__init__(size=(1, 1), borders=False, *args, **kwargs)

        # Loading image states
        self._states = "◜◠◝◞◡◟"  # could use: ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏
        self._delays = [0.2, 0.1, 0.1, 0.2, 0.1, 0.1]
        self._current_state = 0

        # Timer
        self._timer = ttk.TTkTimer()
        self._timer.timeout.connect(self._timer_update)
        self._timer.start(self._delays[self._current_state])

    def _timer_update(self) -> None:
        self._current_state += 1
        if self._current_state == len(self._states):
            self._current_state = 0
        self._timer.start(self._delays[self._current_state])
        self.update()

    @override
    def paintEvent(self, canvas: ttk.TTkCanvas):
        """
        Paint Event callback.

        Args:
            canvas: The canvas object used to draw the widget.
        """

        char = self._states[self._current_state]
        if not self._timer.is_alive():
            char = "•"
        canvas.drawChar((0, 0), char)

    def start(self) -> None:
        """Starts or restarts the loading spinner animation."""
        self._timer_update()

    def stop(self) -> None:
        """Stops the loading spinner animation."""
        self._timer.stop()
