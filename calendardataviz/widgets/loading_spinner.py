import TermTk as ttk
from typing_extensions import Any, override


class LoadingSpinnerWidget(ttk.TTkFrame):
    """Loading widget, with a loading spinner"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
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
        self._alive = True

    def _timer_update(self) -> None:
        self._alive = True
        self._current_state = (self._current_state + 1) % len(self._states)
        self._timer.start(self._delays[self._current_state])
        self.update()

    @override
    def paintEvent(self, canvas: ttk.TTkCanvas):
        """
        Paint Event callback.

        Args:
            canvas: The canvas object used to draw the widget.
        """

        if self._alive:
            canvas.drawChar((0, 0), self._states[self._current_state])
        else:
            canvas.drawChar((0, 0), "•")
        

    def start(self) -> None:
        """Starts or restarts the loading spinner animation."""
        self._timer_update()

    def stop(self) -> None:
        """Stops the loading spinner animation."""
        self._timer.stop()
        self._alive = False
