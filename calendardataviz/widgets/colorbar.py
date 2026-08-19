from collections.abc import Sequence
from typing import Any, override

import TermTk as ttk

from calendardataviz.inspector_abc import InspectorABC


class ColorBarWidget(ttk.TTkFrame):
    """Color bar widget, displaying the percentage
    colors given by an inspector.
    """

    def __init__(
        self,
        inspector: InspectorABC,
        *args: Sequence[Any],
        **kwargs: dict[str, Any],
    ) -> None:
        """
        Args:
            inspector: Inspector class associated to the loaded calendar.
            args: Arguments passed to the ttk.TTkWindow parent class.
            kwargs: Arguments passed to the ttk.TTkWindow parent class.
        """

        # Call parent
        size = kwargs.get("size", (10, 20))
        if "size" in kwargs:
            del kwargs["size"]
        if "border" in kwargs:
            del kwargs["border"]
        super().__init__(size=size, border=False, *args, **kwargs)

        self._colors = inspector.as_color_bar(self.height())

    @override
    def paintEvent(self, canvas: ttk.TTkCanvas):
        """
        Paint Event callback.

        Args:
            canvas: The canvas object used to draw the widget.
        """

        super().paintEvent(canvas)

        height = self.height() - 1
        for y, color in enumerate(self._colors):
            canvas.drawTTkString((0, y), color)
            if y == 0 or y % 5 == 0 or y == height:
                canvas.drawText(
                    pos=(1, y),
                    text=f"-{y / height * 100:.0f}%",
                )

    @override
    def resizeEvent(self, w, h):
        """Override to stop resizing."""
        return True
