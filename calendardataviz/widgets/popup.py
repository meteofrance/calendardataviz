from collections.abc import Sequence
from typing import Any, override

import TermTk as ttk


class PopupWindowWidget(ttk.TTkWindow):
    """Popup window, with a scroll area."""

    def __init__(
        self,
        text: str,
        distance_to_screen_bottom: int,
        *args: Sequence[Any],
        **kwargs: dict[str, Any],
    ) -> None:
        """
        Args:
            text: Content of the popup's body.
            distance_to_screen_bottom: Used to compute the
                window's allowed height.
            args: Arguments passed to the ttk.TTkWindow parent class.
            kwargs: Arguments passed to the ttk.TTkWindow parent class.
        """

        self._text = text
        width: int = max(len(line) for line in text.split("\n"))
        height: int = len(text.split("\n"))
        if "title" in kwargs:
            width = max(width, len(kwargs["title"]) + 3)
        window_height = min(
            height + 4,
            distance_to_screen_bottom,
        )

        super().__init__(
            size=(width + 3, window_height),
            flags=ttk.TTkK.WindowFlag.WindowCloseButtonHint,
            *args,
            **kwargs,
        )

        # Instantiate the scroll area
        scroll_area = ttk.TTkScrollArea(
            parent=self,
            visible=True,
            pos=(0, 0),
            size=(width + 1, window_height - 4),
            verticalScrollBarPolicy=ttk.TTkK.ScrollBarAlwaysOn,
        )
        ttk.TTkLabel(
            parent=scroll_area.viewport(),
            text=text,
        )

    @override
    def resizeEvent(self, w, h):
        """Override to stop resizing."""
        return True
